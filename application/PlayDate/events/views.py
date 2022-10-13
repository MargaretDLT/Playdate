# from cgitb import lookup
from multiprocessing import Event
from unicodedata import category
from unittest import result
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from events.models import EventRegistration
from home.forms import addressForm
from home.models import User, Profile
from events.forms import eventForm
from events.forms import GroupEventForm, PublicEventForm
from events.models import Publicevent, Address, Event
from django.views.decorators.csrf import csrf_exempt

import requests
import json

# Create your views here.

# Display public events for general user
def publicevents(request):
    publicevents = Publicevent.objects.all()
    # return render(request,"events/publicevents.html",{'publicevent':publicevent})
    return render(request, "events/publicevents.html",{'publicevents': publicevents})

# Display all the events for user to register
def membersevents(request):
    user=request.user
    publicevents= Publicevent.objects.all()
    if user.is_authenticated:
        eventregistrations=EventRegistration.objects.filter(user=user).values_list('event')
        profile = Profile.objects.get(profileID=user)
        print(eventregistrations)
        events=Event.objects.all().exclude(event_id__in = eventregistrations)
        print(events)
        # Check if the user is verified
        regUser = False
        if user.is_authenticated:
            isVerified = Profile.objects.get(profileID=request.user)
            if isVerified.is_verified == True:
                regUser = True
        else:
            regUser = False
        return render(request, "membersevents.html",{'events':events,'publicevents':publicevents,'user':user,'profile':profile,'regUser':regUser})
    
    
    return render(request, "membersevents.html",{'publicevents':publicevents,'user':user})

def eventRegistration(request,event_id):
    user=request.user
    if request.method == 'POST':
        event=Event.objects.get(event_id=event_id)
        event_registration=EventRegistration.objects.create(user=user,event=event)
        # return render(request,"memberEvent1.html",{'event':event,'registration':event_registration})
        return  HttpResponseRedirect('/events/%s/'%event.event_id)

def deleteEvent(request,event_id):
    eventInstance=Event.objects.get(event_id=event_id)
    events=EventRegistration.objects.filter(event=eventInstance).delete()
    eventInstance.delete()
    
    return HttpResponseRedirect('/events/my-events/')

def editEvent(request,event_id):  
    user=request.user
    eventInstance=Event.objects.get(event_id=event_id)
    if eventInstance.user != user:
        return HttpResponseForbidden()
    form=eventForm(request.POST or None, instance=eventInstance)
    addressInstance=Address.objects.get(event=eventInstance)
    addrform=addressForm(request.POST or None, instance=addressInstance)
    if request.POST and form.is_valid():
        print("save")
        form.save()
        return HttpResponseRedirect('/events/my-events/')
    return render(request,'editEvent.html',{'eventform':form,'addressform':addrform})

def publicEvent1(request, event_id):
    event=Publicevent.objects.get(public_event_id=event_id)
    return render(request, "publicevent.html",{'event':event})


def memberEvent1(request):
    return render(request, "memberEvent1.html")


def signUpSucceed(request):
    return render(request, "signUpSucceed.html")


def myEvent(request):
    user=request.user
    events=Event.objects.filter(user=user)
    eventregistrations=EventRegistration.objects.filter(user=user)

    # Check if the user is verified
    regUser = False
    if request.user.is_authenticated:
        isVerified = Profile.objects.get(profileID=request.user)
        if isVerified.is_verified == True:
            regUser = True
    else:
        regUser = False
    
    return render(request, "myEvent.html",{'registered_events':eventregistrations,'events':events, 'user':user, 'regUser': regUser})


def createPublicEvent(request):
    form = PublicEventForm()
    if request.method == 'POST':
        form = PublicEventForm(request.POST, request.FILES)
        if form.is_valid():
            instancePE = form.save(commit=False)
            instancePE.banner = None
            instancePE.banner = request.FILES['banner']
            instancePE.save()

            PublicEvent = Publicevent.objects.get(
                public_event_id=instancePE.public_event_id)
            return render(request, 'events/createPublicEventSuccess.html', {'PublicEvent': PublicEvent})

    return render(request, 'events/createPublicEventForm.html', {'publicEventForm': form})


@csrf_exempt
def createGroupEvent(request):
    if request.method == 'POST':
        form = GroupEventForm(request.POST)
        if form.is_valid():
            a = Address.objects.create(street=request.POST.get('street'),
                                       city=request.POST.get('city'),
                                       state=request.POST.get('state'),
                                       country=request.POST.get('country'),
                                       zipcode=request.POST.get('zipcode'))
            ge = Event.objects.create(name=request.POST.get(
                'name'), category=request.POST.get('category'), address=a)

            return HttpResponseRedirect('/thanks/')
    else:
        form = GroupEventForm()

    return render(request, "/events/createEvent.html", {'form': form})


def filter(request):
    if request.method == 'POST':
        select = request.GET.get('select')


# Definition to create new user event
def createEvent(request):
    # context={}
    user=request.user
    regUser = None
    if request.user.is_authenticated:
        regUser = Profile.objects.get(profileID=user)
    else:
        regUser = None
    if request.method == 'POST':
        eventform= eventForm(request.POST,request.FILES)
        addressform=addressForm(request.POST)
        
        if addressform.is_valid() and eventform.is_valid():
            address= addressform.save()
            event=eventform.save(commit=False)
            # image upload process
            event.banner = None
            if len(request.FILES) == 0:
                event.banner = None
            else:
                event.banner = request.FILES['banner']
            event.user=user
            event.address=address
            event.save()
            # print(event.event_id)
            event=Event.objects.get(event_id=event.event_id)
            event_registration=EventRegistration.objects.create(user=user,event=event)
    
            return HttpResponseRedirect('/events/%s/'%event.event_id)
    else:
        eventform=eventForm()
        addressform=addressForm()
    # context['form']=form
   
    return render(request, 'events/createEvent.html',{'eventform': eventform,'addressform':addressform, 'regUser':regUser})

# Definition to view Event page
def viewEvent(request, event_id):
    event=Event.objects.get(event_id=event_id)
    print(event.name)
    user=request.user
    isEventAdmin = (event.user == user) or (event.group_admin == user) 
    registration=EventRegistration()
    isRsvp=0
    # try:
    registration=EventRegistration.objects.filter(user__exact=user).filter(event__exact=event_id)
    # except:
        
        # print(registration)
    if registration is not None:
        print("$$$$$")
        isRsvp=registration.first()
    attendees=EventRegistration.objects.filter(event=event_id)
    # print (registrations)
    return render(request, 'events/createdEvent.html', {'event' : event, 'attendees': attendees,'isRsvp':isRsvp, 'user': user, 'isEventAdmin': isEventAdmin})

def eventRegistrationEdit(request):
    print( "Received Event Registration")
    if request.method == "POST":
        requestData = json.loads(request.body)
        print ("User: " + str(request.user) + " (Auth: " + str(request.user.is_authenticated) + ")")
        print ("Data: ")
        print(requestData)
        if request.user.is_authenticated:
            responseData = { 'request': requestData }
            if requestData['operation'] == "DELETE":
                try: 
                    print ("Received DELETE")
                    rsvp = EventRegistration.objects.get(registration_id = requestData['rsvpID'])
                    print ("Got RSVP")
                    if rsvp.user == request.user or request.user == rsvp.event.user:
                        # The proper accounts are triggering this RSVP deletion
                        print ("Attempting DELETE")
                        rsvp.delete()
                        print("DELETE Successful!")
                        return JsonResponse(responseData, status=200)
                    else:

                        # Deletion requested from improper user
                        errDict = {
                            'message': "Our records indicate that user "+str(request.user.pk)+" does not have permission to remove user "+str(rsvp.user.pk)+" from event "+str(rsvp.event.pk),
                            'err': "Improper permission for requested task."
                        } 
                        responseData['error'] = errDict
                        return JsonResponse(responseData, status=500)
                except Exception as exc:
                    errDict = {
                        'message': 'An exception occurred during RSVP Deletion: '+str(type(exc)),
                        'err': str(exc)
                    }
                    responseData['error'] = errDict
                    return JsonResponse(responseData, status=500)
        return JsonResponse({'message': "Please login."}, status=403)
    return JsonResponse({ 'message': "Please use POST."}, status=403)

# Returns Search result for events
def events(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        filter = request.GET.get('category')

        submitbutton = request.GET.get('submit')
        print(query)

        if query is not None:
            if filter == 'All':
               # query databse to check if matching city, zipcode, or street

                lookups = Q(address__city__icontains=query) | Q(address__zipcode__icontains=query) | Q(
                    address__country__icontains=query) | Q(address__street__icontains=query)

                results = Publicevent.objects.filter(lookups)

            elif filter == 'Kids':
                # query databse to check if matching city, zipcode, or street

                lookups = Q(address__city__icontains=query) | Q(address__zipcode__icontains=query) | Q(
                    address__country__icontains=query) | Q(address__street__icontains=query)

                results = Publicevent.objects.filter(
                    lookups).filter(Q(category__icontains='kids'))
                print(filter)
            else:
                lookups = Q(address__city__icontains=query) | Q(address__zipcode__icontains=query) | Q(
                    address__country__icontains=query) | Q(address__street__icontains=query)

                results = Publicevent.objects.filter(
                    lookups).filter(Q(category__icontains='pets'))
                print(filter)

            context = {'results': results,
                       'submitbutton': submitbutton}
            return render(request, 'events/events.html', context)

    else:
        return render(request, 'events/events.html')
    return render(request, 'events/events.html')
# def events(request):
#     if request.method == 'GET':
#         query= request.GET.get('q')
#         filter= request.GET.get('category')

#         submitbutton= request.GET.get('submit')
#         print(query)

#         if query is not None:
#             if filter=='All':
#            #query databse to check if matching city, zipcode, or street

#                 lookups= Q(address__city__icontains=query) | Q(address__zipcode__icontains=query) | Q(address__country__icontains=query) | Q(address__street__icontains=query)

#                 results= Publicevent.objects.filter(lookups)

#             elif filter=='Kids':
#             #query databse to check if matching city, zipcode, or street

#                 lookups= Q(address__city__icontains=query) | Q(address__zipcode__icontains=query) | Q(address__country__icontains=query) | Q(address__street__icontains=query)

#                 results= Publicevent.objects.filter(lookups).filter(Q(category__icontains = 'kids'))
#                 print(filter)
#             else:
#                 lookups= Q(address__city__icontains=query) | Q(address__zipcode__icontains=query) | Q(address__country__icontains=query) | Q(address__street__icontains=query)

#                 results= Publicevent.objects.filter(lookups).filter(Q(category__icontains = 'pets'))


#             context={'results': results,
#                      'submitbutton': submitbutton}

#             return render(request, 'events/events.html', context)


#     else:
#         return render(request, 'events/events.html')
#     return render(request, 'events/events.html')
