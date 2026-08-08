from django.contrib import admin


class TradeAdminSite(admin.AdminSite):
    site_header = 'UCTrade Trade Admin'


trade_admin_site = TradeAdminSite(name='trade_admin')
