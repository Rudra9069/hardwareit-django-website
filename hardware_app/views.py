from django.http import HttpRequest,HttpResponse
from django.shortcuts import render, redirect
import re
from .models import *
from django.db.models import Q



# Signin Page------------------------------------------------------------
def signup_page(request : HttpRequest):

    msg = ""
    

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')
        dob = request.POST.get('dob')
        pwd = request.POST.get('pwd')
        c_pwd = request.POST.get('c_pwd')
        gender = request.POST.get('gender')

        if not all([name,email,contact_no,dob,pwd,c_pwd,gender]): 
            msg = "All fields are required!"
            popup = True
            return render(request, 'signup.html',{"msg":msg , "popup":popup})

        else:
            email_verify = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            password_verify = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'

            if len(contact_no) != 10:
                msg = "Contact no must be of 10 digits"
                popup = True
                return render(request, 'signup.html',{"msg":msg , "popup":popup})

            elif not re.match(email_verify, email):
                msg = "Email not Valid"
                popup = True
                return render(request, 'signup.html',{"msg":msg , "popup":popup})
            
            elif not re.match(password_verify,pwd):
                msg = "Password must contain, atleast uppercase, lowercase, digit, special character"
                popup = True
                return render(request, 'signup.html',{"msg":msg , "popup":popup})

            elif pwd != c_pwd:
                msg = "Password does not match"
                popup = True
                return render(request, 'signup.html',{"msg":msg , "popup":popup})
        
            else:
                user.objects.create(
                    name=name,
                    email=email,
                    contact_no=contact_no,
                    dob=dob,
                    pwd=pwd,
                    gender=gender
                )
                msg = "Register Done"
                popup = True

                return redirect('login_page')

    return render(request, 'signup.html',{"msg":msg})


# Login Page---------------------------------------------------------------------------

def login_page(request : HttpRequest):

    msg = ""
    
    if request.method == 'POST':
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')

        myuser = user.objects.filter(email=email, pwd=pwd).first()

        if myuser:
            msg = f"Welcome {myuser.name}, you have logged in successfully."

            # Create response and set cookies
            response = redirect('home_page')
            response.set_cookie(key='email', value=email)
            return response

        else:
            msg = "Invalid Email or Password"

    return render(request, 'login.html', {"msg": msg})

# Logout-----------------------------------------------------------------------
def logout(request : HttpRequest):
    response = redirect('home_page')
    response.delete_cookie('email')
    return response

def home_page(request : HttpRequest):

    email = request.COOKIES.get('email')
    myuser = None

    if email:
        myuser = user.objects.filter(email=email).first()

    return render(request, 'home.html', {"myuser":myuser})

def products_page(request : HttpRequest):

    email = request.COOKIES.get('email')
    myuser = None

    if email:
        myuser = user.objects.filter(email=email).first()

    query = request.GET.get("q", "")
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )

    return render(request, "products.html", {
        "products": products,
        "query": query,
        "myuser":myuser,
    })

def about_page(request : HttpRequest):

    email = request.COOKIES.get('email')
    myuser = None

    if email:
        myuser = user.objects.filter(email=email).first()

    return render(request, 'about.html', {"myuser":myuser})

def contact_page(request):

    email = request.COOKIES.get('email')
    myuser = None

    if email:
        myuser = user.objects.filter(email=email).first()

    if request.method == "POST":
        Contact.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            message=request.POST["message"]
        )
    return render(request, "contact.html", {"myuser":myuser})


def add_to_cart(request, product_id):
    email = request.COOKIES.get('email')

    if not email:
        return redirect('login_page')

    myuser = user.objects.filter(email=email).first()
    if not myuser:
        return redirect('login_page')

    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=myuser, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_page')

def remove_from_cart(request, cart_id):
    email = request.COOKIES.get('email')
    if not email:
        return redirect('login_page')

    cart_item = Cart.objects.get(id=cart_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart_page')


def cart_page(request):
    email = request.COOKIES.get('email')
    if not email:
        return redirect('login_page')

    myuser = user.objects.filter(email=email).first()
    if not myuser:
        return redirect('login_page')

    cart_items = Cart.objects.filter(user=myuser)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "myuser": myuser
    })

def delete_from_cart(request, cart_id):
    email = request.COOKIES.get('email')
    if not email:
        return redirect('login_page')

    Cart.objects.filter(id=cart_id).delete()
    return redirect('cart_page')


def checkout_page(request):
    email = request.COOKIES.get('email')
    if not email:
        return redirect('login_page')

    myuser = user.objects.filter(email=email).first()
    if not myuser:
        return redirect('login_page')

    cart_items = Cart.objects.filter(user=myuser)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "checkout.html", {
        "myuser": myuser,
        "cart_items": cart_items,
        "total_price": total_price
    })

def place_order(request):
    if request.method != "POST":
        return redirect("checkout_page")

    email = request.COOKIES.get("email")
    if not email:
        return redirect("login_page")

    myuser = user.objects.filter(email=email).first()
    if not myuser:
        return redirect("login_page")

    cart_items = Cart.objects.filter(user=myuser)
    if not cart_items.exists():
        return redirect("cart_page")

    address = request.POST.get("address")
    if not address:
        return redirect("checkout_page")

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # 1️⃣ Create Order
    order = Order.objects.create(
        user=myuser,
        total_amount=total_price,
        address=address,
        status="Done"
    )

    # 2️⃣ Create Order Items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity
        )

    # 3️⃣ Clear Cart
    cart_items.delete()

    # 4️⃣ Redirect to success page
    return redirect("order_success", order_id=order.id)

def order_success(request, order_id):
    email = request.COOKIES.get("email")
    if not email:
        return redirect("login_page")

    myuser = user.objects.filter(email=email).first()
    order = Order.objects.get(id=order_id, user=myuser)

    return render(request, "order_success.html", {
        "order": order,
        "myuser": myuser
    })


