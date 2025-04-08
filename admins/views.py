from django.shortcuts import render,redirect
from django.contrib import messages
from students.models import studentregistermodel

# Create your views here.
def AdminLogin(request):
    return render(request, 'AdminLogin.html', {})


def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)

        # Hardcoded login check
        if usrid == 'admin' and pswd == 'admin':
            # Store user_name in session
            request.session['user_name'] = usrid
            print("Session stored with user_name:", request.session.get('user_name'))  # Debugging line
            return redirect(AdminHome)  # Redirect to Admin Home page
        else:
            messages.success(request, 'Please Check Your Login Details')

    return render(request, 'AdminLogin.html', {})

def AdminHome(request):
    user_name = request.session.get('user_name', None)
    return render(request, 'admins/AdminHome.html',{'user_name': user_name})

 # Assuming this is the model you're working with



from django.db.models import Q  # Import Q to handle complex queries
 # Replace with your actual model

def RegisterUsersView(request):
    # Retrieve the search query from the GET request
    search_query = request.GET.get('search', '').strip()  # Get the search query and strip extra spaces
    print(f"RegisterUsersView: Search Query = {search_query}")  # Debug

    # Filter the data based on the search query
    if search_query:
        data = studentregistermodel.objects.filter(
            Q(name__icontains=search_query) |  # Match name
            Q(email__icontains=search_query) |  # Match email
            Q(mobile__icontains=search_query)  # Match mobile
        ).order_by('-id')  # Order results by ID in descending order
        print(f"RegisterUsersView: Filtered Data Count = {data.count()}")  # Debug
    else:
        data = studentregistermodel.objects.all().order_by('-id')  # Fetch all data if no search query
        print(f"RegisterUsersView: Total Data Count = {data.count()}")  # Debug

    # Pagination: Display 5 users per page
    paginator = Paginator(data, 20)  
    page_number = request.GET.get('page')  # Get the current page number from the URL
    data_page = paginator.get_page(page_number)  # Get the paginated data for the current page
    print(f"RegisterUsersView: Current Page = {data_page.number}, Total Pages = {paginator.num_pages}")  # Debug

    # Determine the starting index for the current page
    start_index = (data_page.number - 1) * paginator.per_page

    # Retrieve 'user_name' from the session for personalized experience
    user_name = request.session.get('user_name', None)

    # Render the template with the data and pagination info
    return render(request, 'admins/viewregisterusers.html', {
        'data': data_page,  # Pass paginated data
        'user_name': user_name,  # Pass user name
        'start_index': start_index,  # Pass starting index for display
        'search_query': search_query  # Pass the search query back to the template
    })



def activate_user(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        user_name = request.session.get('user_name')

        print(f"activate_user: Received activation request for User ID = {id}")  # Debug

        if not user_name:
            print("activate_user: Session expired.")  # Debug
            messages.error(request, "Session expired. Please log in again.")
            return redirect('admin_login')

        if not id:
            print("activate_user: User ID is missing in the request.")  # Debug
            messages.error(request, "User ID is missing.")
            return redirect('admins/viewregisterusers')

        try:
            id = int(id)
        except ValueError:
            print(f"activate_user: Invalid User ID = {id}")  # Debug
            messages.error(request, "Invalid User ID.")
            return redirect('admins/viewregisterusers')

        updated = studentregistermodel.objects.filter(id=id, status='waiting').update(status='activated')

        if updated:
            print(f"activate_user: User ID = {id} activated successfully.")  # Debug
            messages.success(request, f"User with ID {id} has been activated and can now log in.")
        else:
            print(f"activate_user: User ID = {id} activation failed.")  # Debug
            messages.error(request, f"User with ID {id} is either not found or already activated.")

        return redirect('RegisterUsersView')


def BlockUser(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(f"BlockUser: Received block request for User ID = {id}")  # Debug

        if not id:
            print("BlockUser: User ID is missing in the request.")  # Debug
            messages.error(request, "User ID is missing.")
            return redirect('admins/viewregisterusers')

        try:
            id = int(id)
        except ValueError:
            print(f"BlockUser: Invalid User ID = {id}")  # Debug
            messages.error(request, "Invalid User ID.")
            return redirect('admins/viewregisterusers')

        updated = studentregistermodel.objects.filter(id=id, status='activated').update(status='blocked')

        if updated:
            print(f"BlockUser: User ID = {id} blocked successfully.")  # Debug
            messages.success(request, f"User with ID {id} has been blocked.")
        else:
            print(f"BlockUser: User ID = {id} block failed.")  # Debug
            messages.error(request, f"User with ID {id} cannot be blocked or is not activated.")

        return redirect('RegisterUsersView')


def UnblockUser(request):

    if request.method == 'GET':
        id = request.GET.get('uid')
        print(f"UnblockUser: Received unblock request for User ID = {id}")  # Debug

        if not id:
            print("UnblockUser: User ID is missing in the request.")  # Debug
            messages.error(request, "User ID is missing.")
            return redirect('admins/viewregisterusers')

        try:
            id = int(id)
        except ValueError:
            print(f"UnblockUser: Invalid User ID = {id}")  # Debug
            messages.error(request, "Invalid User ID.")
            return redirect('admins/viewregisterusers')

        updated = studentregistermodel.objects.filter(id=id, status='blocked').update(status='activated')

        if updated:
            print(f"UnblockUser: User ID = {id} unblocked successfully.")  # Debug
            messages.success(request, f"User with ID {id} has been unblocked.")
        else:
            print(f"UnblockUser: User ID = {id} unblock failed.")  # Debug
            messages.error(request, f"User with ID {id} cannot be unblocked or is not blocked.")

        return redirect('RegisterUsersView')


from django.shortcuts import render, redirect
from .models import Route
from .forms import RouteForm
from django.shortcuts import render, redirect, get_object_or_404

def add_route(request):
    user_name = request.session.get('user_name', None)
    if not user_name:
        return redirect('login')
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            form = RouteForm()
            messages.success(request,'route added succefully')
  # Redirect to a route list page after saving
    else:
        form = RouteForm()
    return render(request, 'admins/route_form.html', {'form': form})

from django.shortcuts import render
from .models import Route

def viewroutes(request):
    user_name = request.session.get('user_name', None)


    # Fetch all routes added by the admin, ordered by their ID
    routes = Route.objects.all().order_by('id')

    return render(request, 'admins/routes.html', {
        'routes': routes,
        'user_name': user_name
    })
  

def edit_route(request, pk):
    route = get_object_or_404(Route, pk=pk)  # Fetch the route or return 404
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('viewroutes')  # Redirect to route list after updating
    else:
        form = RouteForm(instance=route)
    return render(request, 'admins/route_form.html', {'form': form})

def delete_route(request, pk):
    print("Accessing delete_route")  # Debugging output
    route = get_object_or_404(Route, pk=pk)
    print(f"Route to delete: {route}")  # Debugging output

    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
        return redirect('viewroutes')

    return render(request, 'admins/delete_confirmation.html', {'route': route})
       
from django.shortcuts import render
from students.models import RouteSelection
from django.core.paginator import Paginator
from django.db.models import Q


def BusPassAppliedUsersView(request):
    user_name = request.session.get('user_name', None)
    
    if not user_name:
        return redirect('login')

    # Get the search query from the GET parameters
    search_query = request.GET.get('search', '')

    # Filter the applications based on the search query
    if search_query:
        applications_list = RouteSelection.objects.select_related('applicant', 'route').filter(
            Q(applicant__name__icontains=search_query) | 
            Q(applicant__email__icontains=search_query) | 
            Q(applicant__mobile__icontains=search_query) | 
            Q(route__start_point__icontains=search_query) | 
            Q(route__end_point__icontains=search_query)
        ).order_by('-pass_applied_date')
    else:
        applications_list = RouteSelection.objects.select_related('applicant', 'route').all().order_by('-pass_applied_date')

    print("Filtered Applications: ", applications_list)  # Debug print to check the filtered results

    # Pagination
    paginator = Paginator(applications_list, 5)  # Show 5 applications per page
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)
    
    return render(request, 'admins/bus_pass_applied_users.html', {
        'applications': applications,
        'user_name': user_name,
        'search_query': search_query,
    })

from students.views import UserLoginCheck
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = studentregistermodel.objects.get(email=email)
            return redirect(reset_password, email=email)
        except studentregistermodel.DoesNotExist:
            messages.error(request, 'User does not exist.')
    
    return render(request, 'forgot_password.html')

def reset_password(request, email):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            try:
                user = studentregistermodel.objects.get(email=email)
                user.password = new_password
                user.save()
                messages.success(request, 'Password updated successfully! Please login.')
                return redirect(UserLoginCheck)
            except studentregistermodel.DoesNotExist:
                messages.error(request, 'User does not exist.')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'reset_password.html', {'username': email})