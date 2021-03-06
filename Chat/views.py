from django.shortcuts import render, Http404

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from Manager.manager import *
from django.http import JsonResponse
from django.db.models import Q
from Manager.status import *
import logging
import json

HasOpened = False


def index(request):
    # Obtain the controller
    status = Status()
    # Open the Status Controller
    global HasOpened
    if not HasOpened:
        status.setDaemon(True)
        status.start()
        HasOpened = True
    logging.debug(request.user.is_authenticated)
    # Save the stat for the user who login
    groups = []
    friends = []
    pregroup = ""
    ugender = ""
    usig = ""
    if request.user.is_authenticated():
        status.add_active_user(request.user)
        # load the group info and the friend in Group Friend name
        groups_object = load_group(request.user)
        groups = get_groupname(groups_object)
        friends = load_friend(groups_object[groups.index("Friend")])
        pregroup = "Friend"
        info = UserInfo.objects.get(username=request.user)
        usig = info.signature
        if info.gender != 'N':
            if info.gender == 'F':
                ugender = "Girl"
            else:
                ugender = "Boy"
        else:
            ugender = "Secret"
        # Render it
    return render(request, 'index.html', {
        'request': request,
        'groups': groups,
        'friends': friends,
        'pregroup': pregroup,
        'ugender' : ugender,
        'usig' : usig,
    })


@csrf_exempt
def post(request):
    # Obtain the controller
    status = Status()
    global HasOpened
    if not HasOpened:
        status.setDaemon(True)
        status.start()
        HasOpened = True
        if request.user.is_authenticated():
            status.add_active_user(request.user)
    if not request.user.is_authenticated():
        return HttpResponse(3)
    if status.active_user[request.user.username].rest == 0:
        tu = UserInfo.objects.get(username=request.user)
        tu.state = 'F'
        tu.save()
        logout(request)
        return HttpResponse(3)
    if request.method == 'POST':
        post_type = request.POST.get('post_type')

        # sending chat content to others
        if post_type == 'send_chat':
            if request.user.is_authenticated():
                status.add_active_user(request.user)
            # Insert new chat history to the Chat table
            sender = request.user
            receiver = User.objects.get(username=request.POST.get('receiver'))
            new_chat = Chat.objects.create(
                content=request.POST.get('content'),
                sender=sender,
                receiver=receiver,
            )
            # Update the unread num in FriendRelation table
            fr = FriendRelation.objects.filter(u1_name=sender, u2_name=receiver)
            if len(fr) == 0:
                fr = FriendRelation.objects.filter(u1_name=receiver, u2_name=sender)
                i = fr[0]
                i.u1_chat_num += 1
                i.save()
                # un = fr[0].u1_chat_num + 1
                # fr.update(u1_chat_num=un)
            else:
                i = fr[0]
                i.u2_chat_num += 1
                i.save()
                # un = fr[0].u2_chat_num + 1
                # fr.update(u2_chat_num=un)
            # Add unread flag in the status
            status.add_unread_flag(receiver)
            # return the result
            logging.debug(json.dumps(ChattoJSON(new_chat)))
            return JsonResponse(ChattoJSON(new_chat))

        # refresh the friends list
        elif post_type == 'get_friends':
            if request.user.is_authenticated():
                status.add_active_user(request.user)
            group_name = request.POST.get('groupname')
            friends = load_user_friend(group_name, request.user)
            return JsonResponse(friends, safe=False)

        # click some user to begin chatting
        elif post_type == 'begin_chat':
            res = {}
            if request.user.is_authenticated():
                status.add_active_user(request.user)
            # Obtain the information of the request
            sender = request.user
            receiver = User.objects.get(username=request.POST.get("chatter"))
            # set the status for have read
            fr = FriendRelation.objects.filter(u1_name=sender, u2_name=receiver)
            if len(fr) == 0:
                fr = FriendRelation.objects.filter(u1_name=receiver, u2_name=sender)
                fr.update(u2_chat_num=0)
            else:
                fr.update(u1_chat_num=0)
            # Remove unread flag in the status
            status.remove_unread_flag(receiver)
            # set the least and max default num
            chat_num = request.POST.get("chat_num")
            if chat_num > 20:
                chat_num = 20
            if chat_num < 5:
                chat_num = 5
            # Obtain the last_chat list
            last_chat = Chat.objects.filter(Q(sender=receiver, receiver=sender) | Q(sender=sender, receiver=receiver))
            chats = list(last_chat.order_by('id'))[-chat_num:]
            # Change to JSON
            res["chat"] = ListtoJSON(chats)
            res["info"] = ChattoJSON(UserInfo.objects.get(username=receiver))
            return JsonResponse(res)

        # load more chatting history
        elif post_type == 'load_more':
            if request.user.is_authenticated():
                status.add_active_user(request.user)
            sender = request.user
            receiver = User.objects.get(username=request.POST.get("chatter"))
            last_id = request.POST.get("last_id")
            condition = Q(id__lt=last_id) & (Q(sender=receiver, receiver=sender) | Q(sender=sender, receiver=receiver))
            last_chat = Chat.objects.filter(condition)
            chats = list(last_chat.order_by('id'))[-5:]
            res = ListtoJSON(chats)
            logging.debug(res)
            return JsonResponse(res)

        # polling for new info
        elif post_type == 'fresh_states':
            res = {}
            msg = status.get_user_msg(request.user.username)
            if not msg:
                return JsonResponse(res)
            else:
                res['msg_type'] = msg.msg_type
                res['sender'] = msg.sender
                res['content'] = msg.content
                logging.debug(res)
                return JsonResponse(res)

        # scraping NEW state of your fiends, including
        #       - Group new talk
        #       - pregroup friend
        #       - new chat come
        elif post_type == 'fresh_friends':
            # if not status.active_user[request.user.username].new_chat:
                # return JsonResponse({"friends": False})
            res = {}
            pre_group = request.POST.get("pregroup")
            friends = fresh_user_friend(pre_group, request.user)
            friends.reverse()
            other_group = Group.objects.exclude(username=request.user, group_name=request.POST.get("pregroup"))
            # check group new
            groups = []
            for i in other_group:
                condition = ((Q(u1_group=i, u1_chat_num__gt=0)) | (Q(u2_group=i, u1_chat_num__gt=0)))
                groups.append(len(FriendRelation.objects.filter(condition)))
            # check present chatter new
            pre_chats = []
            pre_chatter = request.POST.get("prechatter")
            pc = User.objects.filter(username=pre_chatter)
            if len(pc) != 0:
                con = (Q(u1_name=pc[0], u2_name=request.user)) | (Q(u1_name=request.user, u2_name=pc[0]))
                fr = FriendRelation.objects.get(con)
                num = fr.u1_chat_num + fr.u2_chat_num
                if fr.u1_chat_num != 0 and fr.u1_name == request.user or fr.u2_chat_num != 0 and fr.u2_name == request.user:
                    if fr.u1_name == request.user:
                        fr.u1_chat_num = 0
                    elif fr.u2_name == request.user:
                        fr.u2_chat_num = 0
                    fr.save()
                    l = Chat.objects.filter(Q(sender=pc[0], receiver=request.user) | Q(sender=request.user, receiver=pc[0]))
                    pre_chats = list(l.order_by('id'))[-num:]
            res["friends"] = friends
            res["groups"] = groups
            res["chats"] = ListtoJSON(pre_chats)
            return JsonResponse(res)
            # return JsonResponse([friends, groups], safe=False)
    else:
        raise Http404


@csrf_exempt
def command(request):
    # Obtain the controller
    status = Status()
    user = request.user
    global HasOpened
    if not HasOpened:
        status.setDaemon(True)
        status.start()
        HasOpened = True
    if request.user.is_authenticated():
        status.add_active_user(request.user)
    elif request.user.username not in status.active_user.keys():
        status.add_user(request.user)
    if not request.user.is_authenticated():
        return HttpResponse(3)
    if status.active_user[request.user.username].rest == 0:
        tu = UserInfo.objects.get(username=request.user)
        tu.state = 'F'
        tu.save()
        logout(request)
        return HttpResponse(3)
    if request.method == 'POST':
        command_type = request.POST.get('command_type')
        # sending chat content to others
        if command_type == 'delete_friend':
            friend = User.objects.get(username=request.POST.get('friend'))
            df = FriendRelation.objects.get(Q(u1_name=request.user, u2_name=friend) | Q(u1_name=friend, u2_name=request.user))
            df.delete()
            msg = UserMessage(request.user.username, "", MSG.FRIEND_DELETE)
            if status.put_user_msg(request.POST.get('friend'), msg):
                logging.debug(msg)
                return HttpResponse(1)
            return HttpResponse(0)
        elif command_type == 'add_friend':
            friend = User.objects.get(username=request.POST.get('friend'))
            condition = Q(u1_name=friend,u2_name=request.user) | Q(u1_name=request.user, u2_name=friend)
            if len(FriendRelation.objects.filter(condition)) != 0:
                return HttpResponse(0)
            status = Status()
            msg = UserMessage(request.user.username,  request.POST.get('remark'), MSG.FRIEND_REQUEST)
            if status.put_user_msg(request.POST.get('friend'), msg):
                logging.debug(msg)
                return HttpResponse(1)
            return HttpResponse(0)
        elif command_type == 'search_friend':
            res = {}
            friend = User.objects.filter(username__contains=request.POST.get('friend'))
            if len(friend) == 0:
                res['res'] = 2
                return JsonResponse(res)
            else:
                res['res'] = 1
                ui = []
                for i in list(friend)[:10]:
                    if i.username != request.user.username:
                        ui.append(UserInfo.objects.get(username=i))
                res['data'] = ListtoJSON(ui)
                return JsonResponse(res)
        elif command_type == 'move_friend':
            friend = User.objects.get(username=request.POST.get('friend'))
            group = Group.objects.get(username=request.user, group_name=request.POST.get('group'))
            df = FriendRelation.objects.get(Q(u1_name=request.user, u2_name=friend) | Q(u1_name=friend, u2_name=request.user))
            if df.u1_name == request.user:
                df.u1_group = group
            else:
                df.u2_group = group
            df.save()
            return HttpResponse(1)
        elif command_type == 'add_group':
            if len(Group.objects.filter(username=request.user, group_name=request.POST.get('group'))) == 0:
                Group.objects.create(username=request.user, group_name=request.POST.get('group'))
                return HttpResponse(1)
            else:
                return HttpResponse(0)
        elif command_type == 'delete_group':
            group = Group.objects.filter(username=request.user, group_name=request.POST.get('group'))
            tgroup = Group.objects.filter(username=request.user, group_name=request.POST.get('tgroup'))
            if len(group) != 0 and len(tgroup) != 0 and group != tgroup:
                fl = FriendRelation.objects.filter(u1_name=request.user, u1_group=group[0])
                for f in fl:
                    f.u1_group = tgroup[0]
                    f.save()
                fl = FriendRelation.objects.filter(u2_name=request.user, u2_group=group[0])
                for f in fl:
                    f.u2_group = tgroup[0]
                    f.save()
                group[0].delete()
                return HttpResponse(1)
            else:
                return HttpResponse(0)
        elif command_type == 'accept_msg':
            status = Status()
            msg = UserMessage(request.user.username, "", MSG.FRIEND_ACCEPT)
            friend = User.objects.get(username=request.POST.get("friend"))
            f2 = Group.objects.get(username=request.user, group_name="Friend")
            f1 = Group.objects.get(username=friend, group_name="Friend")
            FriendRelation.objects.create(u1_name=friend, u1_group=f1, u2_name=request.user, u2_group=f2)
            if status.put_user_msg(request.POST.get('friend'), msg):
                logging.debug(msg)
                return HttpResponse(1)
            return HttpResponse(0)
    else:
        raise Http404


@csrf_exempt
def upload_file(request):
    # Obtain the controller
    status = Status()
    global HasOpened
    if not HasOpened:
        status.setDaemon(True)
        status.start()
        HasOpened = True
    if request.user.is_authenticated():
        status.add_active_user(request.user)
    elif request.user.username not in status.active_user.keys():
        status.add_user(request.user)
    if status.active_user[request.user.username].rest == 0:
        tu = UserInfo.objects.get(username=request.user)
        tu.state = 'F'
        tu.save()
        logout(request)
    import Image
    import time
    photo = request.FILES.get('image', None)
    logging.debug(request.FILES)
    if photo:
        photoname = '%s.%s' % (request.user.username, 'png')
        img = Image.open(photo)
        logging.debug(photoname)
        img.save('static/images/' + photoname)
    return HttpResponseRedirect("../")
