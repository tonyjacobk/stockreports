from  .morningbeat   import classify_reports,company_reports
from .comp_and_brok import get_company_and_broker
from .tel_utils import preprocessName,get_details_from_other_report_name
def get_broker_and_company_names(fname1):
    fname=preprocessName(fname1)
    print(fname)
    u=classify_reports(fname)
    print ("Report is of type",u)
    if u in ["compbrok","onreport","compres","othcomp"]:
      ret_val,comp_det=get_company_and_broker(fname,u)
      print("Vals",comp_det,fname)
    if u in ["Others"]:
      ret_val,comp_det=get_company_and_broker(fname,"othcomp")
