#!/usr/bin/env python
# coding:utf-8
import sys
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import click
import json
from certbot_aliyun_cdn.client import CDN as certbot_cdn
reload(sys)
sys.setdefaultencoding("utf-8")


class CDN(certbot_cdn):
    def DescribeDomainCertificateInfo(self, domain):
        info = self.call("DescribeDomainCertificateInfo", DomainName=domain)
        return info


class SSL():
    def __init__(self, access_key_id, access_key_secret):
        client = AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
        self.client = client

    def CommonRequest(self):
        request = CommonRequest()
        request.set_domain('cas.aliyuncs.com')
        request.set_version('2018-07-13')
        return request

    def DeleteUserCertificate(self, CertId):
        request = self.CommonRequest()
        request.set_action_name('DeleteUserCertificate')
        request.add_query_param('CertId', CertId)
        res = self.client.do_action_with_exception(request)
        print(res)

    def DescribeUserCertificateList(self, ShowSize=1, CurrentPage=1):
        request = self.CommonRequest()
        request.set_action_name('DescribeUserCertificateList')
        request.add_query_param('ShowSize', ShowSize)
        request.add_query_param('CurrentPage', CurrentPage)
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def GetAllCertList(self, ShowSize=100):
        total = self.DescribeUserCertificateList().get("TotalCount")
        AllCertList = {}
        for CurrentPage in range(1, total/ShowSize+2):
            res = self.DescribeUserCertificateList(ShowSize=ShowSize,
                                                   CurrentPage=CurrentPage)
            for Certificate in res.get("CertificateList"):
                common = Certificate.get("common")
                name = Certificate.get("name")
                nid = Certificate.get("id")
                endDate = Certificate.get("endDate")
                if common not in AllCertList:
                    AllCertList.setdefault(common,
                                           {
                                            name: {"id": None,
                                                   "endDate": None}})
                else:
                    AllCertList[common][name] = {"id": None, "endDate": None}
                AllCertList[common][name]["id"] = nid
                AllCertList[common][name]["endDate"] = endDate
        return AllCertList


@click.command()
@click.option("--access_key_id")
@click.option("--access_key_secret")
@click.option("--do_delete", default=False)
def main(access_key_id, access_key_secret, do_delete):
    ssl = SSL(access_key_id, access_key_secret)
    AllCertList = ssl.GetAllCertList()
    cdn = CDN()
    cdn.set_credentials(access_key_id, access_key_secret)

    for domain in cdn.list_domains():
        CertInfos = cdn.DescribeDomainCertificateInfo(domain).get(
            "CertInfos", {}).get("CertInfo", [])
        AllCertName = AllCertList.get(domain)
        if not AllCertName:
            continue
        AllCertNameKeys = AllCertName.keys()
        for CertInfo in CertInfos:
            InUseCertName = CertInfo.get("CertName")
            AllCertNameKeys.remove(InUseCertName)
        for key in AllCertNameKeys:
            print("starting clean domain: {0}'s cert: {1} endDate: {2} CertId: {3}\
                  ".format(domain, key, AllCertName.get(key).get("endDate"),
                           AllCertName.get(key).get("id")))
            if not do_delete:
                continue
            NeedCleanOldSSLId = AllCertName.get(key).get("id")
            ssl.DeleteUserCertificate(NeedCleanOldSSLId)

if __name__ == "__main__":
    main()
