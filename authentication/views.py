from django.contrib.auth import authenticate, login

def user_auth(request):
    print('request')
    '''
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        print('foo')
    else:
        print('bar')
    '''
    return