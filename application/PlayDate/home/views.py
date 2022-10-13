# home/views.py
#
#   This file stores the views for all the URLs in the home application. The views
# are how the content of each URL is generated - sometimes just rendering an html
# template, sometimes requiring information validation or database access (through
# forms and models.)
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from ipware import get_client_ip
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from events.models import Event, EventRegistration
from groups.models import Member
from . import models
from . import forms

# Session Creation
#  This is used to manage and track sessions.
# Session information is serialized via JSON_Serializer and stored in django_session
# needs fine-tuning in order to better track sessions for unlogged and logged users.


def sessionCreation(request):
    if not request.session.session_key:
        request.session.create()
        # session time is set to 6minutes, needs to be updated
        # request.session.set_expiry(360)
        request.session['visitorIP'] = get_client_ip(request)[0]
        print("session created for IP: ",
              request.session['visitorIP'], " with tracking_key:", request.session.session_key)

# /[serv]/
#  Do we need the commented code?


def home(request):
    sessionCreation(request)
    print("USER SESSION CREATED WITH KEY ID: ", request.session.session_key)
    return render(request, 'home.html')

# /[serv]/login
# TODO: Render invalid password


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            retVals = {
                'username': username,
                'password': password,
                'error': True,
                'modalTitle': 'Invalid Login',
                'modalText': 'The username and password combination that you entered was invalid. Please try again. If this continues, please contact support by clicking the "Contact Us" link at the bottom of the page.',
                'modalBtnText': "Close",
                'modalImmediate': True
            }
            return render(request, 'login.html', retVals)

    context = {}
    return render(request, 'login.html')

# /[serv]/logout/


def logoutPage(request):
    # The following also clears session data
    logout(request)
    return redirect('home')

# /[serv]/register/


def registrationPage(request):
    sessionCreation(request)
    # print(request.session.session_key)
    # print(request.session['visitorIP'])
    user_form = forms.userRegistrationForm()
    accountForm = forms.accountForm()
    if request.method == 'POST':
        # Prepare the session and the forms.
        sessionCreation(request)
        user_form = forms.userRegistrationForm(request.POST)
        accountForm = forms.accountForm(request.POST)
        profileForm = forms.profileForm(request.POST)
        # Check for Validation errors and send them back to the page
        if not user_form.is_valid():
            print(user_form.errors)
            return render(request, 'register.html', {'user_form': user_form, 'accountForm': accountForm, 'feedback': "Error", 'error': user_form.errors})
        elif not accountForm.is_valid():
            print(accountForm.errors)
            return render(request, 'register.html', {'user_form': user_form, 'accountForm': accountForm, 'feedback': "Error", 'error': accountForm.errors})
        elif not profileForm.is_valid():
            print(profileForm.errors)
            return render(request, 'register.html', {'user_form': user_form, 'accountForm': accountForm, 'feedback': "Error", 'error': profileForm.errors})
        else:
            # Save the user, the account, and log in the new user
            user = user_form.save()
            account = accountForm.save(commit=False)
            account.accountID = user
            account.save()
            account.trackingID = request.session.session_key
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request, username=username, password=password)
            account.save()
            if user is not None:
                login(request, user)
                # trying to figure out how to put the next 3 lines above 'if user is not None'
                profile = profileForm.save(commit=False)
                profile.profileID = request.user
                profile.save()

                # this next section seems superfluous...
                userData = request.user
                userInfo = User.objects.get(username=username)
                accountInfo = models.Account.objects.get(accountID=userInfo.id)
                login(request, user)
                userID = userInfo.id
                lastLogin = userInfo.last_login
                is_superuser = userInfo.is_superuser
                fname = userInfo.first_name
                lname = userInfo.last_name
                email = userInfo.email
                gender = accountInfo.gender
                dob = accountInfo.dob

                return render(request, "home.html", {'userID': userID, 'fname': fname, 'lname': lname, 'email': email, 'gender': gender, 'dob': dob, 'message': "You've successfully created an account. Welcome to PlayDate!"})
            else:
                # There was an error authenticating the newly registered user.
                return render(request, "invalidLogin.html")
    # If just a GET request, then send them the html.
    return render(request, 'register.html', {'user_form': user_form, 'accountForm': accountForm})

# /[serv]/profileEdit/


def profileEditPage(request):
    profile = models.Profile.objects.get(profileID=request.user)
    print(profile.avatar)
    profileForm = forms.profileForm()
    if request.method == 'POST':
        profileForm = forms.profileForm(request.POST, request.FILES)
        if profileForm.is_valid():
            instance = profileForm.save(commit=False)
            instance.profileID = request.user
            # Delete current avatar and replace it with request.FILES['avatar']
            instance.avatar = None
            instance.avatar = request.FILES['avatar']
            print(instance.avatar)
            # Update profile in database
            instance.save()

            profile = models.Profile.objects.get(profileID=request.user)
            return render(request, 'profilePage.html', {'profileForm': profileForm, 'profile': profile})
    else:
        profileForm = forms.profileForm()
    return render(request, 'profileEdit.html', {'profileForm': profileForm, 'profile': profile})

# /[serv]/profile


def profilePage(request):
    verForm = forms.profilePage_VerificationForm()
    # If GET, send the user, profile, account and dependents
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect("home")
        else:
            profile = models.Profile.objects.get(profileID=request.user)
            account = models.Account.objects.get(accountID=request.user)
            try:
                dependents = models.Dependent.objects.filter(profile=profile)
            except:
                dependents = None
            finally:
                print("Profile-----------------------------")
                print(profile)
                print("Account-----------------------------")
                print(account)
                print("Dependents--------------------------")
                print(dependents)
                return render(request, 'profilePage.html', {'user': request.user, 'account': account, 'profile': profile, 'dependents': dependents, 'verForm': verForm})
    # If Post, we will update User, Profile, and Account and send
    # everything to the client with a success message
    if request.method == "POST":
        print(request.POST)
        if not request.user.is_authenticated:
            return redirect("home")

        # First grab info from the request for each form
        account_data = {
            'gender': request.POST['inputGender'], 'dob': request.POST['inputDOB']}
        user_data = {'username': request.POST['inputUserName'], 'first_name': request.POST['inputFirstName'],
                     'last_name': request.POST['inputLastName'], 'email': request.POST['inputEmail']}
        profile_data = {'profileDesc': request.POST['inputDescription']}
        address_data = {'street': request.POST['inputStreet'], 'city': request.POST['inputCity'],
                        'state': request.POST['inputState'], 'country': request.POST['inputCountry'], 'zipcode': request.POST['inputZipCode']}

        # Prepare error message
        errorMsg = {
            'error': False,
            'errors': None
        }

        # Deal with user form
        user = request.user
        user_form = forms.profilePage_UserForm(user_data, instance=user)
        if not user_form.is_valid():
            errorMsg = {
                'error': True,
                'errors': user_form.errors
            }
        else:
            user = user_form.save()

        # Deal with account form
        account = models.Account.objects.get(accountID=user)
        account_form = forms.profilePage_AccountForm(
            account_data, instance=account)
        if not account_form.is_valid():
            errorMsg = {
                'error': True,
                'errors': user.errors
            }
        else:
            account_form.save()

        # Deal with profile form
        profile = models.Profile.objects.get(profileID=request.user)
        profile_form = forms.profilePage_ProfileForm(
            profile_data, instance=profile)
        if not profile_form.is_valid():
            errorMsg = {
                'error': True,
                'errors': profile_form.errors
            }
        else:
            profile = profile_form.save()

        # Deal with address form
        address = profile.address
        if address is None:
            address = models.Address()
            address.street = ""
            address.city = ""
            address.state = ""
            address.zipcode = 0
            address.country = ""
            address.save()
            profile.address = address
            profile.save()
        address_form = forms.profilePage_AddressForm(
            address_data, instance=address)
        if not address_form.is_valid():
            errorMsg = {
                'error': True,
                'errors': address_form.errors
            }
        else:
            address = address_form.save()

        # Get dependents
        dependents = models.Dependent.objects.filter(profile=profile)

        # Debug statements
        print("User--------------------------------")
        print(user)
        print("Profile-----------------------------")
        print(profile)
        print("Account-----------------------------")
        print(account)
        print("Dependents--------------------------")
        print(dependents)

        # Compile data for render
        if errorMsg['error']:
            retVals = {
                'user': user,
                'account': account,
                'profile': profile,
                'dependents': dependents,
                'verForm': verForm,
                'modalTitle': "Error",
                'modalText': str(errorMsg['errors']),
                'modalBtnText': "Close",
                'modalImmediate': True}
        else:
            retVals = {
                'user': user,
                'account': account,
                'profile': profile,
                'dependents': dependents,
                'verForm': verForm,
                'modalTitle': "Success!",
                'modalText': "Successfully saved your Account Details.",
                'modalBtnText': "Close",
                'modalImmediate': True}
        return render(request, 'profilePage.html', retVals)


def accountSettings(request, user_id):
    if not request.user.is_authenticated:
        return redirect('home')
    myProfile = models.Profile.objects.get(profileID=request.user)
    myAccount = models.Account.objects.get(accountID=request.user)
    targetUser = User.objects.filter(id=user_id)
    if len(targetUser) == 0:
        targeetUser = None
    else:
        targetUser = targetUser[0]

    if request.user.id == user_id:
        if 'deleteAccount' in request.POST:
            print("DEV-CONSOLE: Deleting Account...")
            u = User.objects.get(id=user_id)
            logout(request)
            u.delete()
            print("Successfully deleted:", u.username)
            return redirect('home')
        return render(request, "accountSettings.html", {'user_id': user_id, 'myProfile': myProfile, 'myAccount': myAccount})
    return render(request, "accountSettings.html", {'user': targetUser})


def avatarUpload(request):
    if request.user.is_authenticated:
        print("Hit avatarUpload")
        user = request.user
        profile = models.Profile.objects.get(profileID=request.user)
        dependents = models.Dependent.objects.filter(profile=profile)
        account = models.Account.objects.get(accountID=user)
        if request.method == 'POST':
            # Unload the image
            avatarForm = forms.profilePage_AvatarForm(
                request.POST, request.FILES, instance=profile)
            if avatarForm.is_valid():
                avatarProfile = avatarForm.save(commit=False)
                if len(request.FILES) == 0:
                    avatarProfile.avatar = None
                else:
                    avatarProfile.avatar = request.FILES['avatar']
                avatarProfile.save()
                retVals = {
                    'user': user,
                    'account': account,
                    'profile': avatarProfile,
                    'dependents': dependents,
                    'modalTitle': "Success!",
                    'modalText': "Successfully updated your avatar.",
                    'modalBtnText': "Close",
                    'modalImmediate': True}
                return render(request, 'profilePage.html', retVals)
        else:
            retVals = {
                'user': user,
                'account': account,
                'profile': profile,
                'dependents': dependents,
                'modalTitle': "Error",
                'modalText': "Please use a POST request",
                'modalBtnText': "Close",
                'modalImmediate': True}
            return render(request, 'profilePage.html', retVals)
    else:
        return redirect('home')


# AJAX Endpoint
def dependents(request):
    print("Received Dependents Request")
    # Expect the info of a dependent
    if request.method == "POST":
        data = json.loads(request.body)
        print("User: " + str(request.user) +
              " (Auth: " + str(request.user.is_authenticated) + ")")
        print("Data: ")
        print(data)
        if request.user.is_authenticated:
            # Update the dependent model list as necessary
            profile = models.Profile.objects.get(profileID=request.user)
            depID = data['dependent']['id']
            depData = {
                'name': data['dependent']['name'],
                'type': data['dependent']['type'],
                'dob': data['dependent']['dob'],
                'interests': data['dependent']['interests'],
                'profile': profile
            }

            # Dependent Action: DELETE -------------------------------------
            if data['state'] == "DELETE":
                print("Mode: DELETE")
                try:
                    models.Dependent.objects.get(dependent_id=depID).delete()
                    retVal = {
                        'message': "Successfully deleted dependent"
                    }
                    print("Dependent deletion successful")
                    return JsonResponse(retVal, status=200)
                except Exception as exc:
                    retVal = {
                        'message': 'An exception occurred during dependent deletion',
                        'err': str(exc)
                    }
                    print("Dependent deletion failed")
                    print(retVal['err'])
                    return JsonResponse(retVal, status=500)

            # Dependent Action: UPDATE -------------------------------------
            elif data['state'] == "UPDATE":
                print("Mode: UPDATE")
                try:
                    dependent = models.Dependent.objects.get(dependent_id=depID)
                    depForm = forms.profilePage_DependentForm(
                        depData, instance=dependent)
                    if depForm.is_valid():
                        dependent = depForm.save()
                        retVal = {
                            'message': "Successfully updated dependent",
                            'id': dependent.dependent_id,
                            'type': dependent.type,
                            'name': dependent.name,
                            'dob': dependent.dob,
                            'interests': dependent.interests,
                            'profile': dependent.profile.pk
                        }
                        print("Dependent update successful")
                        return JsonResponse(retVal, status=200)
                    else:
                        retVal = {
                            'message': "Invalid Input in dependent",
                            'err': str(depForm.errors)
                        }
                        print("Dependent update failed")
                        return JsonResponse(retVal, status=500)

                except Exception as exc:
                    retVal = {
                        'message': 'An exception occurred during dependent update',
                        'err': str(exc)
                    }
                    print("Dependent update failed")
                    print(retVal['err'])
                    return JsonResponse(retVal, status=500)

            # Dependent Action: CREATE -------------------------------------
            else:
                print("Mode: CREATE")
                try:
                    depForm = forms.profilePage_DependentForm(depData)
                    if depForm.is_valid():
                        dependent = depForm.save()
                        retVal = {
                            'message': "Successfully created dependent",
                            'id': dependent.dependent_id,
                            'type': dependent.type,
                            'name': dependent.name,
                            'dob': dependent.dob,
                            'interests': dependent.interests,
                            'profile': dependent.profile.pk
                        }
                        print("Dependent create successful")
                        return JsonResponse(retVal, status=200)
                    else:
                        retVal = {
                            'message': "Invalid Input in dependent",
                            'err': str(depForm.errors)
                        }
                        print("Dependent creation failed")
                        return JsonResponse(retVal, status=500)
                except Exception as exc:
                    retVal = {
                        'message': 'An exception occurred during dependent creation',
                        'err': str(exc)
                    }
                    print("Dependent creation failed")
                    print(retVal['err'])
                    return JsonResponse(retVal, status=500)
        return JsonResponse({'message': "Please login."}, status=403)
    return JsonResponse({'message': "Please use POST."}, status=403)

# /[serv]/verificationUpload


def verificationUpload(request):
    if not request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        profile = models.Profile.objects.get(profileID=request.user)
        verForm = forms.profilePage_VerificationForm(
            request.POST, request.FILES, instance=profile)
        if verForm.is_valid():
            verProfile = verForm.save(commit=False)
            if len(request.FILES) == 0:
                verProfile.verification = None
            else:
                verProfile.verification = request.FILES['verification']
            verProfile.save()
    return redirect("profilePage")


# /[serv]/profile/[int]
# TODO: Will need dependents too.
def profileView(request, profile_id):
    user = User.objects.get(id=profile_id)
    print("User: "+str(user.pk))
    profile = models.Profile.objects.get(profileID=profile_id)
    print("Profile: "+str(profile.pk))
    address = profile.address
    account = models.Account.objects.get(accountID=profile_id)
    print("Account: "+str(account.pk))
    dependents = models.Dependent.objects.filter(profile=profile)
    print("Dependents: "+str(len(dependents)))
    createdEvents = Event.objects.filter(user=user)
    print("Events Created: "+str(len(createdEvents)))
    regEvents = EventRegistration.objects.filter(user=user)
    has_rsvp = False
    rsvpEvents = []
    numEvents = len(regEvents)
    print("Events registered: "+str(numEvents))
    if numEvents > 0:
        has_rsvp = True
        for eventAttending in regEvents:
            print(eventAttending.event.name+" " +
                  str(eventAttending.event.datetime))
            rsvpEvents.append(eventAttending.event)
    print("Has RSVP: "+str(has_rsvp))
    print("Events RSVPd: "+str(len(rsvpEvents)))

    groupQS = Member.objects.filter(member_id=user)

    data = {
        'pUser': user,
        'profile': profile,
        'address': address,
        'account': account,
        'dependents': dependents,
        'createdEvents': createdEvents,
        'hasRSVP': has_rsvp,
        'rsvpEvents': rsvpEvents,
        'regEvents': regEvents,
        'membership': groupQS
    }
    print(data)
    return render(request, 'profileView.html', data)

# NOT RETRIEVABLE


def individuleInfoPage(request):
    return render(request, 'individuleInfo.html')

# /[serv]/helpPage/
# TODO: Needs to be connected with backend
# See: ContactSupport


def helpPage(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            name = request.user.first_name + ' ' + request.user.last_name
            name = name + ' (' + request.user.username + ')'
            email = request.user.email
            print("Support GOT")
            print("Name: "+name)
            print("Email: "+email)
            return render(request, 'helpPage.html', {'name': name, 'email': email})
        return render(request, 'helpPage.html')
    else:
        print('*******************************')
        print('Support Contact form Submitted by ' + request.user.get_username())
        if request.method == 'POST':
            data = {
                'name': request.POST['name'],
                'contact': request.POST['email'],
                'type': request.POST['category'],
                'subject': request.POST['subject'],
                'details': request.POST['message']}
            csForm = forms.supportForm(data)
            # validate the form:
            #  Not actually necessary, but is proper.
            if csForm.is_valid():
                print('Form is valid.')
                ticket = csForm.save(commit=False)

                # Grab Registered user data
                if request.user.is_authenticated:
                    ticket.accountID = request.user
                    print('User is authenticated: ' + request.user.username)

                # Grab General User Data
                ipAddr = request.META['REMOTE_ADDR']
                print('IP Address: ' + str(ipAddr))
                try:  # Grabbing specific users may fail
                    print('Trying to fill General User...')
                    userQuery = models.generalUser.objects.get(ip=ipAddr)
                    print('Query Success...')
                    userInfo = userQuery.first()
                    print('Using general user: ' + userInfo)
                except:  # If we cannot find the general user, make one.
                    print('Exception Caught - Query Error')
                    userInfo = models.generalUser(ip=ipAddr)
                    userInfo.save()
                    print('Using new General User: ' + userInfo.ip)
                else:
                    print("General User found")
                finally:
                    ticket.general = userInfo
                    # Grab Support Staff Data
                    try:  # No Support Staff will throw an exception
                        print('Trying to fill support staff...')
                        staffQuery = models.Supportstaff.objects.all()
                        print('Query Success...')
                        staffInfo = staffQuery.first()
                        print('Using Staff: ' + staffInfo.staff_email + '\n')
                        status = 'Success'
                        ticket.staff = staffInfo
                    except:
                        print("No staff to send support request to")
                        status = 'No Staff'
                    finally:
                        ticket.save()
                        print(ticket)
                        # If we did find staff, attempt the email
                        if status == 'Success':
                            email_subject = 'PlayDate Support #' + \
                                str(ticket.request_id) + ': ' + ticket.name
                            email_content = email_subject + '\n'
                            email_content += 'User: '
                            if request.user.is_authenticated:
                                email_content += request.user.get_username()
                            else:
                                email_content += ipAddr
                            email_content += '\nEmail: ' + ticket.accountID.email + '\n'
                            email_content += 'Category: ' + ticket.get_type_display() + '\n'
                            email_content += 'Details: \n\t' + ticket.details + '\n\n'
                            email_from = 'support@playdate.com'
                            email_to = staffInfo.staff_email
                            print('Email Description: ')
                            print("Subject: " + email_subject)
                            print("Content: " + email_content)
                            print("From: " + email_from)
                            print("To: " + email_to)
                            # Note: this function will not work until SMTP server set up.
                            # For now, fail silently.
                            send_mail(
                                email_subject,
                                email_content,
                                email_from,
                                [email_to],
                                fail_silently=True
                            )
                        # Return the user to the contact support page with a status to be displayed.
                        retVals = {
                            'name': data["name"],
                            'email': data["contact"],
                            'category': data["type"],
                            'subject': data["subject"],
                            'message': data["details"],
                            'modalTitle': "Success!",
                            'modalText': "Your support request has been successfully raised.",
                            'modalBtnText': "Close",
                            'modalImmediate': True}
                        return render(request, 'helpPage.html', retVals)
        return render(request, 'helpPage.html')

# /[serv]/termsofuse/


def termsofuse(request):
    return render(request, 'termsofuse.html')

# /[serv]/privacy/


def privacy(request):
    return render(request, 'privacy.html')

# /[serv]/comeSoon/


def comesoonPage(request):
    return render(request, 'comeSoon.html')

# /[serv]/myGroupsPage
#  TODO: This should be moved to groups application.


def myGroupsPage(request):
    return render(request, 'myGroupsPage.html')

# /[serv]/resetPassword/


def resetPassword(request):
    return render(request, 'resetPassword.html')

# /[serv]/createdGroup/
# TODO: Should be moved to Groups


def createdGroup(request):
    return render(request, 'createdGroup.html')

# /[serv]/createdEvent
# TODO: Should be moved to Events


def createdEvent(request):
    return render(request, 'createdEvent.html')

# NOT RETRIEVABLE
# TODO: Move into help page


def contactSupport(request):
    csForm = forms.supportForm()
    print('*******************************')
    print('Support Contact form Submitted by ' + request.user.get_username())
    if request.method == 'POST':
        print(request.POST)
        csForm = forms.supportForm(request.POST)
        # validate the form:
        #  Not actually necessary, but is proper.
        if csForm.is_valid():
            print('Form is valid.')
            ticket = csForm.save(commit=False)

            # Grab Registered user data
            if request.user.is_authenticated:
                ticket.accountID = request.user
                print('User is authenticated: ' + request.user.username)

            # Grab General User Data
            ipAddr = request.META['REMOTE_ADDR']
            print('IP Address: ' + str(ipAddr))
            try:  # Grabbing specific users may fail
                print('Trying to fill General User...')
                userQuery = models.generalUser.objects.get(ip=ipAddr)
                print('Query Success...')
                userInfo = userQuery.first()
                print('Using general user: ' + userInfo)
            except:  # If we cannot find the general user, make one.
                print('Exception Caught - Query Error')
                userInfo = models.generalUser(ip=ipAddr)
                userInfo.save()
                print('Using new General User: ' + userInfo.ip)
            else:
                print("General User found")
            finally:
                ticket.general = userInfo
                # Grab Support Staff Data
                try:  # No Support Staff will throw an exception
                    print('Trying to fill support staff...')
                    staffQuery = models.Supportstaff.objects.all()
                    print('Query Success...')
                    staffInfo = staffQuery.first()
                    print('Using Staff: ' + staffInfo.staff_email + '\n')
                    status = 'Success'
                    ticket.staff = staffInfo
                except:
                    print("No staff to send support request to")
                    status = 'No Staff'
                finally:
                    ticket.save()
                    print(ticket)
                    # If we did find staff, attempt the email
                    if status == 'Success':
                        email_subject = 'PlayDate Support #' + \
                            str(ticket.request_id) + ': ' + ticket.name
                        email_content = email_subject + '\n'
                        email_content += 'User: '
                        if request.user.is_authenticated:
                            email_content += request.user.get_username()
                        else:
                            email_content += ipAddr
                        email_content += '\nEmail: ' + ticket.accountID.email + '\n'
                        email_content += 'Category: ' + ticket.get_type_display() + '\n'
                        email_content += 'Details: \n\t' + ticket.details + '\n\n'
                        email_from = 'support@playdate.com'
                        email_to = staffInfo.staff_email
                        print('Email Description: ')
                        print("Subject: " + email_subject)
                        print("Content: " + email_content)
                        print("From: " + email_from)
                        print("To: " + email_to)
                        # Note: this function will not work until SMTP server set up.
                        # For now, fail silently.
                        send_mail(
                            email_subject,
                            email_content,
                            email_from,
                            [email_to],
                            fail_silently=True
                        )
                    # Return the user to the contact support page with a status to be displayed.
                    return render(request, 'contactSupport.html', {'csForm': csForm, 'status': status})
    return render(request, 'contactSupport.html', {'csForm': csForm})


# Archived Code
    # userData = request.user
    # if userData.is_authenticated:
    #     userInfo = User.objects.get(username=userData)

    #     accountInfo = models.Account.objects.get(accountID=userInfo.id)

    #     print(userData)
    #     userID = userInfo.id
    #     lastLogin = userInfo.last_login
    #     is_superuser = userInfo.is_superuser
    #     fname = userInfo.first_name
    #     lname = userInfo.last_name
    #     email = userInfo.email

    #     gender = accountInfo.gender
    #     dob = accountInfo.dob
    #     print(is_superuser)
    #     print(lastLogin)
    #     print(userID)
    #     print(gender)
    #     return render(request, 'home/home.html', {'userID': userID, 'fname': fname, 'lname': lname, 'email': email, 'gender': gender, 'dob': dob})
    #     if(request.get('logoutBTN')):
    #         logout(request.user)
    #     return render(request, 'home/logout.html')
    # else:
    #     return render(request, 'home/home.html')
