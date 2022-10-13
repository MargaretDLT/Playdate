#••••••••••••••••••••••••••••••••••••••••••#
# ░█▀▀░█▀▄░█▀█░█░█░█▀█░░░█░█░▀█▀░█▀▀░█░█░█▀▀
# ░█░█░█▀▄░█░█░█░█░█▀▀░░░▀▄▀░░█░░█▀▀░█▄█░▀▀█
# ░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░░░░░░▀░░▀▀▀░▀▀▀░▀░▀░▀▀▀
# Contributor(s): AndrewC,
# Version: 1.8.0
# Homepage: http://bedev.playdate.surge.sh/docs/groups/views
# Description: A core functionality of playdate; the views in this file dictate how groups
# are handled by our application including joining/leaving, posting events/comments,
# CRUD operations on group entities, and groupAdmin functionalities.
#•••••••••••••••••••••••••••••••••••••••••••#
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from home.models import Profile
from . import models
from . import forms

# Searching for Groups function


def Search(request):
    # sampleGroups defines a random list of groups to be suggested to the user.
    # groups = list(models.Group.objects.all())
    sampleGroups = []
    groupMembersList = []
    try:
        groupMembersList = random.sample(
            list(models.Member.objects.filter(~Q(member_id=request.user.id))), 3)
        print(groupMembersList)

    except:
        groupMemberList = []
    for i in groupMembersList:
        print(i)
        sampleGroups.append(
            models.Group.objects.get(group_id=i.group_id_id))

    # print("sample:", sampleGroups)

    # print(sampleGroups)

    if 'search' in request.GET:
        query = request.GET['search'].split()
        print("\nQuery:", query)
        groups = models.Group.objects.filter(tags__name__in=query).distinct()
        print(groups)
        # return render(request, "groups/groupSearch.html", {'groups': groups, 'sampleGroups': sampleGroups})
        return render(request, "groups/groupSearch.html", {'groups': groups})
    return render(request, "groups/groupSearch.html", {'sampleGroups': sampleGroups})


def myGroup(request):
    groupsMemberList = models.Member.objects.filter(member_id=request.user.id)
    groupList = []
    groupMemberCount = []

    # Check if the user is verified
    regUser = False
    if request.user.is_authenticated:
        isVerified = Profile.objects.get(profileID=request.user)
        if isVerified.is_verified == True:
            regUser = True
    else:
        regUser = False

    for x in groupsMemberList:
        groupList.append(x.group_id)

    print(groupList)

    for y in groupList:
        groupMemberCount.append(
            (y, len(models.Member.objects.filter(group_id=y))))

    print("groupMemberCount:", groupMemberCount)

    # print(groupList)
    return render(request, 'groups/myGroup.html', {'groupsMemberList': groupsMemberList, 'groupList': groupList, 'memberCount': groupMemberCount, 'regUser': regUser})


# This view is the main driver for groups; it is by far the biggest view
# It has three parts: 1 for a group member, 1 for an non-member, and 1 for the non-user


def groupView(request, group_id):
    joinGroupForm = forms.joinGroupForm()
    group = models.Group.objects.get(
        group_id=group_id)
    member_list = models.Member.objects.filter(group_id=group_id)
    groupEvents = models.GroupEvent.objects.filter(group=group)
    groupPosts = models.Post.objects.filter(group=group)
    allGroupPosts = models.Post.objects.filter(group=group)
    myProfile = Profile.objects.get(profileID=request.user)
    print(groupEvents, "\n\n")
    profiles = []

    for x in member_list:
        profiles.append(Profile.objects.get(profileID=x.member_id))

    profiles = set(profiles)
    profiles = list(profiles)

    print("profiles:", profiles)

    # Check if the user is verified
    regUser = False
    if request.user.is_authenticated:
        isVerified = Profile.objects.get(profileID=request.user)
        if isVerified.is_verified == True:
            regUser = True
    else:
        regUser = False

    # isMember first checks if the user is logged in, then checks the Member table for the (group_id, user_id), returns True is they are a member
    isMember = False
    if request.user.is_authenticated:
        if len(models.Member.objects.filter(group_id=group_id, member_id=request.user)) == 1:
            isMember = True
            # print(isMember)
    if not request.user.is_authenticated:
        print("user is not authenticated")

    context = {
        'group': group,
        'member_list': member_list,
        'regUser': regUser,
        'isMember': isMember,
        'groupEvents': groupEvents,
        'allGroupPosts': allGroupPosts,
        'groupPosts': groupPosts,
        'joinGroupForm': joinGroupForm,
        'profiles': profiles,
        'myProfile': myProfile,
    }

    # This represents the part of the page for a member of the group.
    # Contains functionality for view/crud posts
    # if isMember == True:
    # The following 2 if-statements correspond to joining a group and leaving a group

    # |\ |/  \|\ | __ |\/||_ |\/||__)|_ |__)
    # | \|\__/| \|    |  ||__|  ||__)|__| \
    if isMember == False:
        if 'joinGroup' in request.POST:
            # verification check
            if regUser == None:
                return redirect('verifyYourself')

            print(request.method)
            joinGroupForm = forms.joinGroupForm(request.POST)
            instanceMember = joinGroupForm.save(commit=False)
            instanceMember.group_id = models.Group.objects.get(
                group_id=group_id)
            instanceMember.member_id = request.user
            instanceMember.save()
            isMember = True
            print(request.user, 'has joined group:', group.group_name)
            # return render(request, "groups/groups.html", context)
            return redirect('groupView', group.group_id)

    # _  _ __     __  __ __  __
    # |\/||_ |\/||__)|_ |__)(_
    # |  ||__|  ||__)|__| \ __)
    if isMember == True:
        if 'mainPage' in request.POST:
            print("DEV-CONSOLE: All Activities Button has been Clicked")
            request.session['group_id'] = group.group_id
            return render(request, "groups/groups.html", context)

        if 'newPost' in request.POST:
            print("DEV-CONSOLE: New Post Button has been Clicked")
            request.session['group_id'] = group.group_id
            return redirect('createGroupPost')

        if 'newGroupEvent' in request.POST:
            print("DEV-CONSOLE: 'New Group Event' Button has been Clicked")
            request.session['group_id'] = group.group_id
            return redirect('createGroupEvent')

        if 'postComment' in request.POST:
            request.session['group_id'] = group.group_id
            request.session['post_id'] = request.POST['postComment']
            print("redirecting user to post ID#:", request.session['post_id'])
            # todo: need to figure out how to get the specific comment id and put it in sessions
            # return HttpResponse("hi")
            return redirect('viewGroupPost')

        if 'eventDetails' in request.POST:
            request.session['group_id'] = group.group_id
            # todo: need to figure out how to get the specific comment id and put it in sessions
            # request.session['post_id'] = post.post_id
            return redirect('viewGroupEvent')

        if 'leaveGroupAdmin' in request.POST:
            models.Group.objects.get(group_id=group_id).delete()
            print("deleting group...")
            return redirect('/')

        if 'leaveGroup' in request.POST:
            models.Member.objects.filter(
                group_id=group_id, member_id=request.user).delete()
            isMember = False
            print(request.user, 'has left group:', group.group_name)
            # return render(request, "groups/groups.html", context)
            return redirect('groupView', group.group_id)
            # return redirect('joinSuccess') //This does not work but should be reimplemented because its better practice

    return render(request, "groups/groups.html", context)


# Viewing a particular post so the user can comment and start a discussion.
def viewGroupPost(request, group_id, post_id):
    createGroupCommentForm = forms.createGroupCommentForm()
    group = models.Group.objects.get(
        group_id=group_id)
    member_list = models.Member.objects.filter(group_id=group_id)
    postObject = models.Post.objects.filter(post_id=post_id)
    # print(postObject)
    # print(postObject[0])
    # print(postObject[0].post_id)
    profiles = []

    for x in member_list:
        profiles.append(Profile.objects.get(profileID=x.member_id))

    profiles = set(profiles)
    profiles = list(profiles)

    # it's implied that isMember would already be true, so we can just write isMember=True
    isMember = False
    if len(models.Member.objects.filter(group_id=group_id, member_id=request.user)) == 1:
        isMember = True

    groupEvents = models.GroupEvent.objects.filter(group=group)
    allGroupPosts = models.Post.objects.filter(group_id=group_id)
    groupPosts = models.Post.objects.filter(post_id=post_id)
    groupPostComments = models.groupPostComment.objects.filter(post_id=post_id)

    context = {
        'group': group,
        'member_list': member_list,
        'isMember': isMember,
        'groupEvents': groupEvents,
        'allGroupPosts': allGroupPosts,
        'groupPosts': groupPosts,
        'groupPostComments': groupPostComments,
        'createGroupCommentForm': createGroupCommentForm,
        'profiles': profiles,
        'postObject': postObject,
    }

    if isMember == False:
        if 'joinGroup' in request.POST:
            print(request.method)
            joinGroupForm = forms.joinGroupForm(request.POST)
            instanceMember = joinGroupForm.save(commit=False)
            instanceMember.group_id = models.Group.objects.get(
                group_id=group_id)
            instanceMember.member_id = request.user
            instanceMember.save()
            isMember = True
            print(request.user, 'has joined group:', group.group_name)
            return render(request, "groups/groups.html", context)

    if 'mainPage' in request.POST:
        print("DEV-CONSOLE: All Activities Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('groupView', group.group_id)

    if 'allEvents' in request.POST:
        print("DEV-CONSOLE: All Events Button has been Clicked")
        request.session['group_id'] = group.group_id
        return render(request, "groups/groups.html", context)

    if 'allPosts' in request.POST:
        print("DEV-CONSOLE: All Posts Button has been Clicked")
        request.session['group_id'] = group.group_id
        return render(request, "groups/groups.html", context)

    if 'newPost' in request.POST:
        print("DEV-CONSOLE: New Post Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('createGroupPost')

    if 'newGroupEvent' in request.POST:
        print("DEV-CONSOLE: New Group Event Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('createGroupEvent')

    if 'leaveGroupAdmin' in request.POST:
        models.Group.objects.get(group_id=group_id).delete()
        print("deleting group...")
        return redirect('/')
#########################
    if 'editPost' in request.POST:
        print("DEV-CONSOLE: 'New Group Event' Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('groupView', group.group_id)
        # return redirect('createGroupEvent')

    # done
    if 'deletePost' in request.POST:
        print("deleting post...")
        models.Post.objects.filter(post_id=post_id).delete()
        print("post deleted")
        request.session['group_id'] = group.group_id
        allGroupPosts = models.Post.objects.filter(group_id=group_id)
        return redirect('groupView', group.group_id)
        # return render(request, "groups/groups.html", context)

    if 'reportPost' in request.POST:
        request.session['group_id'] = group.group_id
        # todo: need to figure out how to get the specific comment id and put it in sessions
        # request.session['post_id'] = post.post_id
        return redirect('viewGroupEvent')
########################

    if 'leaveGroup' in request.POST:
        models.Member.objects.filter(
            group_id=group_id, member_id=request.user).delete()
        isMember = False
        print(request.user, 'has left group:', group.group_name)
        request.session['group_id'] = group.group_id

        return render(request, "groups/viewThread.html", context)
        # return redirect('joinSuccess') //This does not work but should be reimplemented because its better practice

    if 'postComment' in request.POST:
        createGroupCommentForm = forms.createGroupCommentForm(
            request.POST)
        if createGroupCommentForm.is_valid():
            instanceComment = createGroupCommentForm.save(commit=False)
            instanceComment.post_id = models.Post.objects.get(
                post_id=postObject[0].post_id)
            instanceComment.user = request.user
            group = models.Group.objects.get(group_id=group_id)
            instanceComment.save()

            # update comments to include the new comment
            groupPostComments = models.groupPostComment.objects.filter(
                post_id=postObject[0].post_id)
            print(groupPostComments)

            return render(request, "groups/viewThread.html", context)
        elif not forms.createGroupCommentForm.is_valid():
            print("FORM NOT VALID:", forms.createGroupCommentForm.errors,
                  "non-field errors:", forms.createGroupCommentForm.non_field_errors)

    return render(request, "groups/viewThread.html", context)
# Viewing a particular event where the user can RSVP or comment


def viewGroupEvent(request, group_id, event_id):
    # Initialization variables
    # This view will have 2 forms, one for comments and one to retrieve the RSVP list
    createGroupEventCommentForm = forms.createGroupEventCommentForm()
    GroupRSVPForm = forms.GroupRSVPForm()
    group = models.Group.objects.get(
        group_id=group_id)
    member_list = models.Member.objects.filter(group_id=group_id)
    RSVP_list = models.RSVP.objects.filter(
        group_id=group_id, event_id=event_id)
    eventObject = models.GroupEvent.objects.filter(event_id=event_id)

    profiles = []

    for x in member_list:
        profiles.append(Profile.objects.get(profileID=x.member_id))

    profiles = set(profiles)
    profiles = list(profiles)

    isRSVP = None
    # print(postObject)
    # print(postObject[0])
    # print(postObject[0].post_id)

    # it's implied that isMember would already be true, so we can just write isMember=True
    isMember = False
    if len(models.Member.objects.filter(group_id=group_id, member_id=request.user)) == 1:
        isMember = True

    if len(models.RSVP.objects.filter(group_id=group_id, event_id=event_id, rsvp_id=request.user)) == 1:
        isRSVP = True
    else:
        isRSVP = False

    # groupEvents = models.GroupEvent.objects.filter(group=group)  # not needed
    groupEvents = models.GroupEvent.objects.filter(event_id=event_id)
    groupEventComments = models.groupEventComment.objects.filter(
        event_id=event_id)
    allGroupEvents = models.GroupEvent.objects.filter(group_id=group.group_id)

    groupPosts = models.Post.objects.filter(group=group)

    context = {
        'group': group,
        'member_list': member_list,
        'isMember': isMember,
        'groupEvents': groupEvents,
        'groupEventComments': groupEventComments,
        'allGroupEvents': allGroupEvents,
        'RSVP_list': RSVP_list,
        'createGroupEventCommentForm': createGroupEventCommentForm,
        'isRSVP': isRSVP,
        'profiles': profiles,
        'eventObject': eventObject,
    }

    # Page Functions
    if isMember == False:
        if 'joinGroup' in request.POST:
            print(request.method)
            joinGroupForm = forms.joinGroupForm(request.POST)
            instanceMember = joinGroupForm.save(commit=False)
            instanceMember.group_id = models.Group.objects.get(
                group_id=group_id)
            instanceMember.member_id = request.user
            instanceMember.save()
            isMember = True
            print(request.user, 'has joined group:', group.group_name)
            return render(request, "groups/groups.html", context)

    if 'mainPage' in request.POST:
        print("DEV-CONSOLE: All Activities Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('groupView', group.group_id)

    if 'newPost' in request.POST:
        print("DEV-CONSOLE: New Post Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('createGroupPost')

    if 'newGroupEvent' in request.POST:
        print("DEV-CONSOLE: New Group Event Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('createGroupEvent')

    if 'leaveGroupAdmin' in request.POST:
        models.Group.objects.get(group_id=group_id).delete()
        print("deleting group...")
        return redirect('/')

    if 'leaveGroup' in request.POST:
        models.Member.objects.filter(
            group_id=group_id, member_id=request.user).delete()
        isMember = False
        print(request.user, 'has left group:', group.group_name)
        request.session['group_id'] = group.group_id

        return render(request, "groups/groups.html", context)
        # return redirect('joinSuccess') //This does not work but should be reimplemented because its better practice
    # RSVP Button

#########################
    if 'editEvent' in request.POST:
        print("DEV-CONSOLE: 'New Group Event' Button has been Clicked")
        request.session['group_id'] = group.group_id
        return redirect('createGroupEvent')

    # done
    if 'deleteEvent' in request.POST:
        models.GroupEvent.objects.filter(event_id=event_id).delete()
        request.session['group_id'] = group.group_id
        allGroupEvents = models.GroupEvent.objects.filter(
            group_id=group.group_id)
        return redirect('groupView', group.group_id)
        # return render(request, "groups/groups.html", context)

    if 'reportEvent' in request.POST:
        request.session['group_id'] = group.group_id
        # todo: need to figure out how to get the specific comment id and put it in sessions
        # request.session['post_id'] = post.post_id
        return redirect('viewGroupEvent')
########################
    if 'RSVP' in request.POST:
        print(request.method)
        GroupRSVPForm = forms.GroupRSVPForm(request.POST)
        instanceRSVP = GroupRSVPForm.save(commit=False)
        instanceRSVP.group_id = models.Group.objects.get(
            group_id=group_id)
        instanceRSVP.rsvp_id = request.user
        instanceRSVP.event_id = models.GroupEvent.objects.get(
            event_id=event_id)
        instanceRSVP.save()
        RSVP_list = models.RSVP.objects.filter(
            group_id=group_id, event_id=event_id)

        isRSVP = True
        groupEventComments = models.groupEventComment.objects.filter(
            event_id=event_id)
        print(request.user, 'has RSVPd for group:',
              group.group_name, " event:", eventObject)
        request.session['group_id'] = group.group_id
        request.session['event_id'] = event_id
        return redirect('viewGroupEvent', group.group_id, event_id)

        # return render(request, "groups/viewGroupEvent.html", {'group': group, 'groupEventComments': groupEventComments, 'member_list': member_list, 'isMember': isMember, 'groupEvents': groupEvents, 'groupPosts': groupPosts, 'groupEventComments': groupEventComments, 'RSVP_list': RSVP_list, 'createGroupEventCommentForm': createGroupEventCommentForm, 'isRSVP': isRSVP})

    if 'unRSVP' in request.POST:
        models.RSVP.objects.filter(
            group_id=group_id, event_id=event_id, rsvp_id=request.user).delete()
        isRSVP = False
        RSVP_list = models.RSVP.objects.filter(
            group_id=group_id, event_id=event_id)
        groupEventComments = models.groupEventComment.objects.filter(
            event_id=event_id)

        print(request.user, 'has unRSVPd:', eventObject)
        request.session['group_id'] = group.group_id
        request.session['event_id'] = event_id
        return redirect('viewGroupEvent', group.group_id, event_id)

        # return render(request, "groups/viewGroupEvent.html", {'group': group, 'member_list': member_list, 'isMember': isMember, 'groupEvents': groupEvents, 'groupPosts': groupPosts, 'groupEventComments': groupEventComments, 'RSVP_list': RSVP_list, 'createGroupEventCommentForm': createGroupEventCommentForm, 'isRSVP': isRSVP})

    # Event Comments
    if 'postComment' in request.POST:
        createGroupEventCommentForm = forms.createGroupEventCommentForm(
            request.POST)
        print(createGroupEventCommentForm)
        print(request.POST)

        if createGroupEventCommentForm.is_valid():
            instanceComment = createGroupEventCommentForm.save(commit=False)
            instanceComment.event_id = models.GroupEvent.objects.get(
                event_id=eventObject[0].event_id)
            instanceComment.user = request.user
            instanceComment.group = group
            instanceComment.save()

            # update comments to include the new comment
            groupEventComments = models.groupEventComment.objects.filter(
                event_id=eventObject[0].event_id)
            print(groupEventComments)
            RSVP_list = models.RSVP.objects.filter(
                group_id=group_id, event_id=event_id)

            return render(request, "groups/viewGroupEvent.html", context)

        elif not createGroupEventCommentForm.is_valid():
            print("FORM NOT VALID:", forms.createGroupEventCommentForm.errors,
                  "non-field errors:", forms.createGroupEventCommentForm.non_field_errors)

    return render(request, "groups/viewGroupEvent.html", context)


def createGroupPost(request):
    group = models.Group.objects.get(group_id=request.session['group_id'])
    member_list = models.Member.objects.filter(group_id=group.group_id)
    isMember = True
    groupEvents = models.GroupEvent.objects.filter(group=group)
    groupPosts = models.Post.objects.filter(group=group)

    createGroupPostForm = forms.createGroupPostForm()
    if request.method == 'POST':
        createGroupPostForm = forms.createGroupPostForm(
            request.POST, request.FILES)
        if createGroupPostForm.is_valid():
            instanceGroupPost = createGroupPostForm.save(commit=False)
            instanceGroupPost.user = request.user
            instanceGroupPost.group = group

            # banner upload process
            instanceGroupPost.banner = None
            if len(request.FILES) == 0:
                instanceGroupPost.banner = None
            else:
                instanceGroupPost.banner = request.FILES['banner']

            instanceGroupPost.save()

            # Group/member/isMember is stored inside the session, the following clears the session incase
            # the user wants to create a post/event for a different group.
            #del request.session['group_id']
            return redirect('groupView', group.group_id)
            # return render(request, "groups/groups.html", {'group': group, 'member_list': member_list, 'isMember': isMember, 'groupEvents': groupEvents, 'groupPosts': groupPosts})
        elif not createGroupPostForm.is_valid():
            print("FORM NOT VALID:", createGroupPostForm.errors,
                  "non-field errors:", createGroupPostForm.non_field_errors)

    return render(request, "groups/createGroupPost.html", {"createGroupPostForm": createGroupPostForm, 'group': group})

# For creating a group event


def createGroupEvent(request):
    group = models.Group.objects.get(group_id=request.session['group_id'])
    member_list = models.Member.objects.filter(group_id=group.group_id)
    isMember = True
    groupEvents = models.GroupEvent.objects.filter(group=group)
    groupPosts = models.Post.objects.filter(group=group)

    createGroupEventForm = forms.createGroupEventForm()
    if request.method == 'POST':
        createGroupEventForm = forms.createGroupEventForm(
            request.POST, request.FILES)
        # for debugging
        # print(request.FILES)
        # print(len(request.FILES))
        if createGroupEventForm.is_valid():
            instanceGroupEvent = createGroupEventForm.save(commit=False)
            instanceGroupEvent.user = request.user
            instanceGroupEvent.group = group

            # banner upload process
            instanceGroupEvent.banner = None
            if len(request.FILES) == 0:
                instanceGroupEvent.banner = None
            else:
                instanceGroupEvent.banner = request.FILES['banner']

            instanceGroupEvent.save()
            return redirect('groupView', group.group_id)

            # Group/member/isMember is stored inside the session, the following clears the session incase
            # the user wants to create a post/event for a different group.

            # return render(request, "groups/groups.html", {'group': group, 'member_list': member_list, 'isMember': isMember, 'groupEvents': groupEvents, 'groupPosts': groupPosts})
        elif not createGroupEventForm.is_valid():
            print("FORM NOT VALID:", createGroupEventForm.errors,
                  "non-field errors:", createGroupEventForm.non_field_errors)

    return render(request, "groups/createGroupEvent.html", {"createGroupEventForm": createGroupEventForm})

# creating the group itself


def createGroup(request):
    createGroupForm = forms.createGroupForm()
    regUser = None
    if request.user.is_authenticated:
        regUser = Profile.objects.get(profileID=request.user)
    print("\ncreateGroup")
    if request.method == 'POST':
        createGroupForm = forms.createGroupForm(request.POST, request.FILES)
        print("FILES", request.FILES)
        if createGroupForm.is_valid():
            instanceGroup = createGroupForm.save(commit=False)
            instanceGroup.group_admin = request.user
            instanceGroup.banner = None
            # the if-stmt below is for when the groupCreator doesn't upload a group banner
            if len(request.FILES) == 0:
                instanceGroup.banner = None
            # otherwise they did upload a banner
            else:
                instanceGroup.banner = request.FILES['banner']
            # put the title in the tags and save Taggit
            instanceGroup.save()
            instanceGroup.getTagsFromContent()
            createGroupForm.save_m2m()

            # Create first member
            memberData = {'group_id': instanceGroup, 'member_id': request.user}
            instanceMember = forms.createFirstMemberForm(memberData)
            instanceMember.save()

            group = models.Group.objects.get(
                group_id=instanceGroup.group_id)
            member_list = models.Member.objects.filter(
                group_id=instanceGroup.group_id)
            # print(member_list.member_id)
            isMember = True

            return redirect('groupView', group_id=instanceGroup.group_id)
            # return render(request, 'groups/groups.html', {'group': group, 'member_list': member_list, 'isMember': isMember})
        retVals = {
            'createGroupForm': createGroupForm, 
            'regUser': regUser,
            'modalTitle': "Error",
            'modalText': createGroupForm.errors.as_text,
            'modalBtnText': "Close",
            'modalImmediate': True
        }
        return render(request, 'groups/createGroup.html', retVals)

    return render(request, 'groups/createGroup.html', {'createGroupForm': createGroupForm, 'regUser': regUser})


def verifyYourself(request):
    return render(request, "groups/verifyYourself.html")

def createGroupTermsandConditions(request):
    return render(request, 'createGroupTermsandConditions.html')


# ░█▀▄░█▀▀░█░█░░░░░█░█░█▀▀░█▀▀░░░█▀█░█▀█░█░░░█░█
# ░█░█░█▀▀░▀▄▀░▄▄▄░█░█░▀▀█░█▀▀░░░█░█░█░█░█░░░░█░
# ░▀▀░░▀▀▀░░▀░░░░░░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀░▀░▀▀▀░░▀░
# The following code was used for prototype/testing purposes, they should be removed in production.
# Remove the following 4 methods once main functionalities are implemented
# and then reroute the URLs to the correct paths

def testGroup(request):
    return render(request, "groups/testGroup.html")

# STATIC: PROTOTYPE USE ONLY


def searchResults(request):
    return render(request, "groups/searchResults.html")

# STATIC: PROTOTYPE USE ONLY


def individualGroup(request):
    return render(request, "groups/individualGroup.html")

# STATIC: PROTOTYPE USE ONLY


# STATIC: PROTOTYPE USE ONLY


def groupStaticTest(request):
    # The code in this function is the startercode for the group search
    # groupList = models.Group.objects.order_by('-group_id')[:]

    # return render(request, "groups/viewAllGroups.html", {'groupList': groupList})
    return render(request, "groups/viewAllGroups.html")
# ••••••


def joinSuccess(request, group_id):
    # ░█▀▄░█▀▀░█▀█░█▀█░▀█▀░█▀▄░░░█▀█░█▀▀░█▀▀░█▀▄░█▀▀░█▀▄
    # ░█▀▄░█▀▀░█▀▀░█▀█░░█░░█▀▄░░░█░█░█▀▀░█▀▀░█░█░█▀▀░█░█
    # ░▀░▀░▀▀▀░▀░░░▀░▀░▀▀▀░▀░▀░░░▀░▀░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀▀░
    # MAINTENENCE - instead for now just redirect user to the updated group page being joining group
    # group = models.Group.objects.get(group_id=group_id)
    # print("hello", group)
    # return render(request, "groups/joinSuccess.html", {'group': group})
    print("Maintenence")
    return HttpResponse("404 Maintenence")
