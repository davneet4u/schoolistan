import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from .models import Payment, CategorySubscription, PaymentCategoryItem
import razorpay
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from utility.pdf_module import html_to_pdf_response, html_to_pdf_buffer
from utility.email_module import send_file_buffer_email
from django.template.loader import get_template
import requests
import base64
import hashlib
import hmac
from post.models import Category, Course
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from acc.models import User
from django.db import connection

ORDER_PRE_STR = settings.ORDER_PRE_STR


# Create your views here.

# @login_required
# def create_order(request):
#     if request.method == 'POST':
#         user = request.user
#         # data = json.loads(request.body)
#         # plan_id = data['plan_id']
#         payment = Payment.objects.create(
#             user_id=user.id, amount=10,
#         )

#         DATA = {
#             "amount": 10 * 100,
#             "currency": "INR",
#             "receipt": f"test-receipt#{payment.id}",
#             "notes": {
#                 "key1": "value3",
#                 "key2": "value2"
#             }
#         }
#         client = razorpay.Client(auth=settings.RAZORPAY_INFOS)
#         res = client.order.create(data=DATA)
#         # print(res)
#         if res['status'] == 'created':
#             payment.razorpay_order_id = res['id']
#             payment.save()
#             order_data = {
#                 'key': settings.RAZORPAY_INFOS[0],
#                 'amount': 10 * 100,
#                 'rzp_order_id': res['id'],
#                 'server_payment_id': payment.id,
#                 'name': user.first_name + ' ' + user.last_name,
#                 'email': user.email,
#                 'contact': "+917206540091"
#             }
#             return JsonResponse({"detail": "Order created successfully", "data": order_data}, status=201)
#         return JsonResponse({"detail": "Something went wrong"}, status=500)


def razorpay_webhook(request):
    pass



# def payment_success(request):
#     if request.method == 'PUT':
#         data = json.loads(request.body)
#         client = razorpay.Client(auth=settings.RAZORPAY_INFOS)
#         try:
#             verification = client.utility.verify_payment_signature({
#                 'razorpay_order_id': data['razorpay_order_id'],
#                 'razorpay_payment_id': data['razorpay_payment_id'],
#                 'razorpay_signature': data['razorpay_signature']
#             })
#             if verification:
#                 payment = Payment.objects.get(
#                     razorpay_order_id=data['razorpay_order_id']
#                 )
#                 payment.razorpay_payment_id = data['razorpay_payment_id']
#                 payment.status = 1
#                 payment.save()
#                 return JsonResponse({"detail": "Information added successfully"}, status=200)
#         except razorpay.errors.SignatureVerificationError:
#             pass
#         return JsonResponse({"detail": "Information verification failed"}, status=500)


# --------------------------------------------------------------
@login_required
def create_order(request):
    if request.method == 'POST':
        cf_domain = "api" if settings.CASH_FREE_MODE == "production" else settings.CASH_FREE_MODE
        user = request.user

        data = json.loads(request.body)

        if data['product_type'] != "course" or not data['product_ids']:
            raise Http404
        
        if not data['product_ids']:
            return JsonResponse({"msg": "Something went wrong", "data": {}}, status=500)
        
        courses = Course.objects.raw(f"SELECT * FROM courses WHERE id IN ({data['product_ids']})")

        amount = 0
        payment = Payment.objects.create(
            user_id=user.id, amount=amount, status=0, product_type="category"
        )

        for course in courses:
            amount += course.price
            PaymentCategoryItem.objects.create(
                payment_id=payment.id, user_id=user.id, title = course.name, status=payment.status,
                category_id=course.category_id, course_id=course.id, validity=course.validity, amount=course.price
            )
        
        payment.amount = amount
        payment.save()

        # creating order for cashfree
        url = f"https://{cf_domain}.cashfree.com/pg/orders"
        headers = {
            # "accept": "application/json",
            "Content-Type": "application/json",
            "x-api-version": "2022-09-01",
            "x-client-id": settings.CASH_FREE_APP_ID,
            "x-client-secret": settings.CASH_FREE_SECRET_KEY
        }
        data = {
            "order_id": f"{ORDER_PRE_STR}{payment.id}",
            "order_amount": payment.amount,
            "order_currency": "INR",
            "order_note": f"schoolistan@{payment.id}",
            "customer_details": {
            "customer_id": f"{user.id}",
                "customer_name": f"{user.first_name} {user.last_name}".strip(),
                "customer_email": user.email,
                "customer_phone": user.mobile if user.mobile and len(user.mobile) == 10 else ""
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            cf_res_data = response.json()
            # print(cf_res_data)
            payment.cf_order_id = cf_res_data['cf_order_id']
            payment.order_id = cf_res_data['order_id']
            payment.payment_session_id = cf_res_data['payment_session_id']
            payment.order_note = cf_res_data['order_note']
            payment.save()
            order_data = {
                "payment_session_id": cf_res_data['payment_session_id'],
                "mode": settings.CASH_FREE_MODE,
                "return_url": f"{request.scheme}://{request.META['HTTP_HOST']}/payments/success" + '?order_id={order_id}'
            }
            return JsonResponse({"msg": "Order created successfully", "data": order_data}, status=201)
        return JsonResponse({"msg": "Something went wrong"}, status=500)
    else:
        return JsonResponse({"msg": "Method not allowed", "data": {}}, status=405)


def generate_cashfree_signature(timestamp, payload):
    message = bytes(timestamp, 'utf-8')+payload
    secretkey=bytes(settings.CASH_FREE_SECRET_KEY,'utf-8') #Get Secret_Key from Cashfree Merchant Dashboard.
    signature = base64.b64encode(hmac.new(secretkey, message, digestmod=hashlib.sha256).digest())
    computed_signature = str(signature, encoding='utf8')
    return computed_signature #compare with "x-webhook-signature"


@csrf_exempt
def cashfree_webhook_success(request):
    if request.method == 'POST':
        expected_signature = request.META['HTTP_X_WEBHOOK_SIGNATURE']
        generated_signature = generate_cashfree_signature(request.META['HTTP_X_WEBHOOK_TIMESTAMP'], request.body)
        if generated_signature == expected_signature:
            data = json.loads(request.body)
            if data['type'] == 'PAYMENT_SUCCESS_WEBHOOK' and data['data']['payment']['payment_status'] == 'SUCCESS':
                order_id = data['data']['order']['order_id']
                if ORDER_PRE_STR not in order_id:
                    return JsonResponse({"msg": "Order does not exists."}, status=204)
                payment_id = order_id.replace(ORDER_PRE_STR, "")
                try:
                    payment = Payment.objects.get(id=payment_id)
                    with connection.cursor() as cursor:
                        cursor.execute(f"""
                            SELECT COUNT(id) AS total FROM category_subscriptions WHERE payment_category_item_id
                            IN (SELECT id FROM payment_category_items WHERE payment_id={payment.id});
                        """)
                        subs_count = cursor.fetchone()[0]
                    if (payment.status == 0 or payment.status == 2) and subs_count == 0:
                        payment.status = 1
                        payment.cf_payment_id = data['data']['payment']['cf_payment_id']
                        payment.save()

                        payment_cat_items = PaymentCategoryItem.objects.filter(payment_id=payment.id)
                        for pay_cat_item in payment_cat_items:
                            # category = Category.objects.get(id=payment.product_id)
                            pay_cat_item.status = payment.status
                            pay_cat_item.save()
                            
                            today_date = datetime.now(tz=ZoneInfo('Asia/Kolkata')).date()
                            try:
                                subscription = CategorySubscription.objects.get(category_id=pay_cat_item.category_id, user_id=payment.user_id)
                                subscription.end_date = subscription.end_date + timedelta(days=pay_cat_item.validity)
                                subscription.payment_category_item_id=pay_cat_item.id
                                subscription.save()
                            except CategorySubscription.DoesNotExist:
                                CategorySubscription.objects.create(
                                    user_id=payment.user_id, category_id=pay_cat_item.category_id,
                                    start_date=today_date,
                                    end_date=today_date + timedelta(days=pay_cat_item.validity),
                                    payment_category_item_id=pay_cat_item.id
                                )
                        generate_and_send_receipt(payment)
                        return JsonResponse({"msg": "Payment information updated successfully."}, status=200)
                    else:
                        return JsonResponse({"msg": "Payment information already updated."}, status=204)
                except Payment.DoesNotExist:
                    return JsonResponse({"msg": "Order does not exists."}, status=404)
            else:
                return JsonResponse({"msg": "Bad request."}, status=400)
        else:
            return JsonResponse({"msg": "Signature not matched."}, status=401)
    return JsonResponse({"msg": "Method not allowed", "data": {}}, status=405)

@csrf_exempt
def cashfree_webhook_failed(request):
    if request.method == 'POST':
        expected_signature = request.META['HTTP_X_WEBHOOK_SIGNATURE']
        generated_signature = generate_cashfree_signature(request.META['HTTP_X_WEBHOOK_TIMESTAMP'], request.body)
        if generated_signature == expected_signature:
            data = json.loads(request.body)
            if data['type'] == 'PAYMENT_FAILED_WEBHOOK' and data['data']['payment']['payment_status'] == 'FAILED':
                order_id = data['data']['order']['order_id']
                if ORDER_PRE_STR not in order_id:
                    return JsonResponse({"msg": "Order does not exists."}, status=204)
                payment_id = order_id.replace(ORDER_PRE_STR, "")
                try:
                    payment = Payment.objects.get(id=payment_id)
                    if payment.status == 0:
                        payment.status = 2
                        payment.cf_payment_id = data['data']['payment']['cf_payment_id']
                        payment.save()
                        return JsonResponse({"msg": "Payment information updated successfully."}, status=200)
                    else:
                        return JsonResponse({"msg": "Payment information already updated."}, status=204)
                except Payment.DoesNotExist:
                    return JsonResponse({"msg": "Order does not exists."}, status=404)
            else:
                return JsonResponse({"msg": "Bad request."}, status=400)
        else:
            return JsonResponse({"msg": "Signature not matched."}, status=401)
    return JsonResponse({"msg": "Method not allowed", "data": {}}, status=405)

@csrf_exempt
def cashfree_webhook_user_dropped(request):
    if request.method == 'POST':
        expected_signature = request.META['HTTP_X_WEBHOOK_SIGNATURE']
        generated_signature = generate_cashfree_signature(request.META['HTTP_X_WEBHOOK_TIMESTAMP'], request.body)
        if generated_signature == expected_signature:
            data = json.loads(request.body)
            if data['type'] == 'PAYMENT_USER_DROPPED_WEBHOOK' and data['data']['payment']['payment_status'] == 'USER_DROPPED':
                order_id = data['data']['order']['order_id']
                if ORDER_PRE_STR not in order_id:
                    return JsonResponse({"msg": "Order does not exists."}, status=204)
                payment_id = order_id.replace(ORDER_PRE_STR, "")
                try:
                    payment = Payment.objects.get(id=payment_id)
                    if payment.status == 0:
                        payment.status = 3
                        payment.cf_payment_id = data['data']['payment']['cf_payment_id']
                        payment.save()
                        return JsonResponse({"msg": "Payment information updated successfully."}, status=200)
                    else:
                        return JsonResponse({"msg": "Payment information already updated."}, status=204)
                except Payment.DoesNotExist:
                    return JsonResponse({"msg": "Order does not exists."}, status=404)
            else:
                return JsonResponse({"msg": "Bad request."}, status=400)
        else:
            return JsonResponse({"msg": "Signature not matched."}, status=401)
    return JsonResponse({"msg": "Method not allowed", "data": {}}, status=405)

def payment_success(request):
    if 'order_id' not in request.GET:
        raise Http404
    payment_id = request.GET['order_id'].replace(ORDER_PRE_STR, "")
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.status == 0:
        messages.error(request, 'Payment pending.')
    elif payment.status == 1:
        messages.success(request, 'Payment completed successfully. Payment receipt has sent to your email.')
    elif payment.status == 2:
        messages.error(request, 'Payment failed.')
    elif payment.status == 3:
        messages.error(request, 'Payment cancelled.')
    else:
        messages.error(request, 'Something went wrong.')
    return redirect('/') 

@login_required
def course_paynow(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    return render(request, 'payments/paynow.html', {
        "course": course, "CASH_FREE_MODE": settings.CASH_FREE_MODE,
        "has_all_profile_info": user.first_name and user.mobile and user.email
    })


@login_required
def fee_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.user_id != request.user.id:
        return HttpResponse("Access denied.", status=403)

    # if payment.status != 1:
    #     return HttpResponse("No payment receipt available.", status=404)
    payment_items = PaymentCategoryItem.objects.filter(payment_id=payment_id)
    # calculations
    taxable_amount_temp = payment.amount * 100 / 118
    taxable_amount = round(taxable_amount_temp, 2)
    total_tax = payment.amount - taxable_amount
    cgst = sgst = round(total_tax / 2, 2)
    pay_user = User.objects.get(id=payment.user_id)

    return html_to_pdf_response('payments/fee-receipt.html', {
        "payment": payment, "payment_items": payment_items, "pay_user": pay_user,
        "taxable_amount": taxable_amount, "cgst": cgst, "sgst": sgst
    })

def generate_and_send_receipt(payment):
    payment_items = PaymentCategoryItem.objects.filter(payment_id=payment.id)
    # calculations
    taxable_amount_temp = payment.amount * 100 / 118
    taxable_amount = round(taxable_amount_temp, 2)
    total_tax = payment.amount - taxable_amount
    cgst = sgst = round(total_tax / 2, 2)
    pay_user = User.objects.get(id=payment.user_id)
    file_obj = html_to_pdf_buffer('payments/fee-receipt.html', {
        "payment": payment, "payment_items": payment_items, "pay_user": pay_user,
        "taxable_amount": taxable_amount, "cgst": cgst, "sgst": sgst
    })
    template = get_template("emails/payment-confirmed.html")
    html  = template.render({
        "curr_date_time": datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%a, %b %d, %Y, %H:%M'),
        "payment": payment
    })
    send_file_buffer_email(pay_user.email, "Payment confirmation", html, file_obj, 'payment-slip.pdf')

