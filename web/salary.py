#coding=utf-8
'''
Created on 2017-03-07

@author: Fusheng
'''

from google.appengine.api import users
from google.appengine.ext import db

from common import decorators, utils, commonInfo, common404
from common.models import IdGen
from django.http import HttpResponse
from django.template import Context, loader
import json

page_size = 10


def calculate_view(request):
    city_name = request.GET.get('city')
    #税前工资
    origin_salary = float(request.GET.get('origin_salary'))
    #社保汇缴基数
    base_social_security = float(request.GET.get('base_social_security'))
    base_house_fund = float(request.GET.get('base_house_fund'))
    is_house_fund = bool(request.GET.get('is_house_fund'))
    is_house_fund_ext = request.GET.get('is_house_fund_ext').encode("utf-8")
    #补充公积金汇缴比例
    rate_house_fund_ext = float(request.GET.get('rate_house_fund_ext'))

    personal_old = base_social_security * 0.08
    personal_med = base_social_security * 0.02
    personal_unemployment = base_social_security * 0.005
    personal_house_fund = base_house_fund * 0.07
    personal_house_fund_ext = 0
    if is_house_fund_ext == 'true':
        personal_house_fund_ext = base_house_fund * rate_house_fund_ext
    personal_prepay_deduct = personal_old + personal_med + personal_unemployment + personal_house_fund + personal_house_fund_ext
    personal_taxable = origin_salary - personal_prepay_deduct
    personal_tax = cal_tax(personal_taxable)
    personal_net_pay = personal_taxable - personal_tax

    org_old = base_social_security * 0.2
    org_med = base_social_security * 0.1
    org_unemployment = base_social_security * 0.01
    org_house_fund = base_house_fund * 0.07
    org_house_fund_ext = 0
    if is_house_fund_ext == 'true':
        org_house_fund_ext = base_house_fund * rate_house_fund_ext
    org_birth = base_social_security * 0.01
    org_work_injury = base_social_security * 0.05
    org_pay = org_old + org_med + org_unemployment + org_house_fund + org_house_fund_ext + org_birth + org_work_injury

    data = {}
    data["origin_salary"] = round(origin_salary, 2)
    data["personal_old"] = round(personal_old, 2)
    data["personal_med"] = round(personal_med, 2)
    data["personal_unemployment"] = round(personal_unemployment, 2)
    data["personal_house_fund"] = round(personal_house_fund, 2)
    data["personal_house_fund_ext"] = round(personal_house_fund_ext, 2)
    data["personal_prepay_deduct"] = round(personal_prepay_deduct, 2)
    data["personal_taxable"] = round(personal_taxable, 2)
    data["personal_tax"] = round(personal_tax, 2)
    data["personal_net_pay"] = round(personal_net_pay, 2)
    data["org_old"] = round(org_old, 2)
    data["org_med"] = round(org_med, 2)
    data["org_unemployment"] = round(org_unemployment, 2)
    data["org_house_fund"] = round(org_house_fund, 2)
    data["org_house_fund_ext"] = round(org_house_fund_ext, 2)
    data["org_birth"] = round(org_birth, 2)
    data["org_work_injury"] = round(org_work_injury, 2)
    data["org_pay"] = round(org_pay, 2)

    return HttpResponse(json.dumps(data))


def salary_view(request, city_name):
    c = Context({})
    add_context_variables(c, city_name, request)
    
    """
       Salary 首页
    """
    t = loader.get_template('web/salary.html')
    return HttpResponse(t.render(c))

        
def add_context_variables(c, city_name, request):
    """
        给Context增加必要的变量
    """
    c['session'] = request.session
    c['city_name'] = city_name;
    c['social_base_max'] = 17817
    c['social_base_min'] = 3563
    c['house_base_max'] = 17817
    c['house_base_mix'] = 2020


def cal_tax(pretax):
    """
        计算个税
    """
    taxable = pretax - 3500
    if taxable <= 1500:
        return taxable * 0.03 - 0
    elif taxable <= 4500:
        return taxable * 0.1 - 105
    elif taxable <= 9000:
        return taxable * 0.2 - 555
    elif taxable <= 35000:
        return taxable * 0.25 - 1005
    elif taxable <= 55000:
        return taxable * 0.3 - 2775
    elif taxable <= 80000:
        return taxable * 0.35 - 5505
    else:
        return taxable * 0.45 - 13505
