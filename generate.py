#!/usr/bin/env python

import click
import tempfile

from certbot_aliyun_cdn.client import CDN


def write_config_ini(email, token, access_key_id, access_key_secret, output):
    content = [
        ("certbot_dns_dnspod:dns_dnspod_email", email),
        ("certbot_dns_dnspod:dns_dnspod_api_token", token),
        ("certbot_alicdn:aliyun_cdn_access_key_id", access_key_id),
        ("certbot_alicdn:aliyun_cdn_access_key_secret", access_key_secret)
    ]
    for key, val in content:
        output.write("{0} = '{1}'\n".format(key, val))


def bash_for_domain(email, config, domain):
    return (
        "certbot run "
        "--email {email} --agree-tos "
        "--authenticator certbot-dns-dnspod:dns-dnspod "
        "--certbot-dns-dnspod:dns-dnspod-credentials {config} "
        "--reinstall --redirect "
        "--installer certbot-aliyun-cdn:aliyun-cdn "
        "--certbot-aliyun-cdn:aliyun-cdn-credentials {config} "
        "--domain {domain}\n"
    ).format(email=email, config=config, domain=domain)


@click.command()
@click.argument("email")
@click.argument("token")
@click.argument("access-key-id")
@click.argument("access-key-secret")
@click.argument("output", type=click.File("wt"))
def generate(email, token, access_key_id, access_key_secret, output):
    tmp = tempfile.NamedTemporaryFile("wt", delete=False)
    with tmp as f:
        write_config_ini(email, token, access_key_id, access_key_secret, f)

    output.write("#!/bin/bash\nset -e\n")

    cdn = CDN()
    cdn.set_credentials(access_key_id, access_key_secret)
    for domain in cdn.list_domains():
        if cdn.check_expiratoin(domain):
            output.write(bash_for_domain(email, tmp.name, domain))


if __name__ == "__main__":
    generate()
