from .version import ERP_VERSION


def erp_version(request):
    return {"ERP_VERSION": ERP_VERSION}

