# -*- coding:utf-8 -*-
from collections import defaultdict
from commandr import Run, command
from datetime import datetime, timedelta
import smtplib
import traceback
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from coin.lib.combination.combination import Combination
from coin.lib.utils import Market, ip
from coin.model.base import get_dbsession
from coin.model.user import UserModel
from coin.model.supervisor_status import SupervisorStatusModel
from coin.model.exception_info import ExceptionInfoModel


# 发件人地址，通过控制台创建的发件人地址
username = 'taohuashan.btc@gmail.com'
# 发件人密码，通过控制台创建的发件人密码
password = 'taohuashan@admin'
# 自定义的回复地址
replyto = 'taohuashan.btc@gmail.com'


def send_email(user, header, text, html):
    """
    发送邮件
    :param user:
    :type user: list of str
    :param header:
    :param text:
    :param html:
    :return:
    """
    # 收件人地址或是地址列表，支持多个收件人，最多30个
    if len(user) == 1:
        rcptto = user[0]
    else:
        rcptto = user
    # 构建alternative结构
    msg = MIMEMultipart('alternative')
    if isinstance(header, unicode):
        msg['Subject'] = Header(header).encode()
    else:
        msg['Subject'] = Header(header.decode('utf-8')).encode()
    msg['From'] = '%s <%s>' % (Header('taohuashan.btc'.decode('utf-8')).encode(), username)
    msg['To'] = ', '.join(rcptto) if isinstance(rcptto, list) else rcptto
    msg['Reply-to'] = replyto
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    # 构建alternative的text/plain部分
    if text:
        textplain = MIMEText(text, _subtype='plain', _charset='UTF-8')
        msg.attach(textplain)
    # 构建alternative的text/html部分
    if html:
        texthtml = MIMEText(html, _subtype='html', _charset='UTF-8')
        msg.attach(texthtml)
    # 发送邮件
    try:
        # client = smtplib.SMTP()
        #python 2.7以上版本，若需要使用SSL，可以这样创建client
        client = smtplib.SMTP_SSL()
        #SMTP普通端口为25或80
        client.connect('smtp.gmail.com', 465)
        #开启DEBUG模式
        client.set_debuglevel(0)
        client.login(username, password)
        #发件人和认证地址必须一致
        #备注：若想取到DATA命令返回值,可参考smtplib的sendmaili封装方法:
        #      使用SMTP.mail/SMTP.rcpt/SMTP.data方法
        client.sendmail(username, rcptto, msg.as_string())
        client.quit()
        print '邮件发送成功！'
    except smtplib.SMTPConnectError, e:
        print '邮件发送失败，连接失败:', e.smtp_code, e.smtp_error
    except smtplib.SMTPAuthenticationError, e:
        print '邮件发送失败，认证错误:', e.smtp_code, e.smtp_error
    except smtplib.SMTPSenderRefused, e:
        print '邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error
    except smtplib.SMTPRecipientsRefused, e:
        print '邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error
    except smtplib.SMTPDataError, e:
        print '邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error
    except smtplib.SMTPException, e:
        print '邮件发送失败, ', e.message
    except Exception, e:
        print '邮件发送异常, ', str(e)


profit_table_header = u"""
    <tr>
    <th>组合</th>
    <th>市场和币种</th>
    <th>总体收益率</th>
    <th>总体收益</th>
    <th>今日币量</th>
    <th>昨日币量</th>
    <th>起始币量</th>
    </tr>
"""


@command('profit')
def report_profit():
    """
    汇报收益
    :return:
    """
    active_combination_list = Combination.all_active()
    user_profit = defaultdict(list)
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    # today_str = '2018-03-31'
    session = get_dbsession()
    res = session.execute('SELECT combination, init_big, init_small, init_bnb, init_huobi, yes_big, '
                          'yes_small, yes_bnb, yes_huobi, now_big, now_small, now_bnb, now_huobi, '
                          'daily_profit_rate, total_profit_rate, daily_profit, total_profit from '
                          'combination_profit where substr(log_time, 1, 10)="{}"'.format(today_str))
    data_res = dict()
    for item in res:
        data_res[item[0]] = item
    for combination_obj in active_combination_list:
        if data_res.get(combination_obj.combination) is None:
            continue
        combination, init_big, init_small, init_bnb, init_huobi, yes_big, yes_small, yes_bnb, \
            yes_huobi, now_big, now_small, now_bnb, now_huobi, daily_profit_rate, total_profit_rate, \
            daily_profit, total_profit = data_res[combination_obj.combination]
        init_point_list = list()
        yes_point_list = list()
        now_point_list = list()
        if combination_obj.first_market == Market.HUOBI or combination_obj.second_market == Market.HUOBI:
            init_point_list.append(u'<p>火币点卡: {}</p>'.format(init_huobi))
            yes_point_list.append(u'<p>火币点卡: {}</p>'.format(yes_huobi))
            now_point_list.append(u'<p>火币点卡: {}</p>'.format(now_huobi))
        if combination_obj.first_market == Market.BINANCE or combination_obj.second_market == Market.BINANCE:
            init_point_list.append(u'<p>bnb: {}</p>'.format(init_bnb))
            yes_point_list.append(u'<p>bnb: {}</p>'.format(yes_bnb))
            now_point_list.append(u'<p>bnb: {}</p>'.format(now_bnb))
        message = u"""
        <tr>
        <td>{id}</td>
        <td><p>{first_market}: {second_market}</p><p>{small_coin}: {big_coin}</p></td>
        <td><p>当日:{daily_profit_rate}%</p><p>总体:{total_profit_rate}%</p></td>
        <td><p>当日:{daily_profit}</p><p>总体:{total_profit}</p></td>
        <td><p>{big_coin}:{now_big}</p><p>{small_coin}:{now_small}</p>{now_point}</td>
        <td><p>{big_coin}:{yes_big}</p><p>{small_coin}:{yes_small}</p>{yes_point}</td>
        <td><p>{big_coin}:{init_big}</p><p>{small_coin}:{init_small}</p>{init_point}</td>
        </tr>
        """.format(id=combination_obj.id, small_coin=combination_obj.small_coin, big_coin=combination_obj.big_coin,
                   init_big=init_big, init_small=init_small, yes_big=yes_big, yes_small=yes_small,
                   now_big=now_big, now_small=now_small, daily_profit=daily_profit,
                   total_profit=total_profit, daily_profit_rate='%.3f' % (daily_profit_rate * 100),
                   total_profit_rate='%.3f' % (total_profit_rate * 100),
                   init_point=u''.join(init_point_list), yes_point=u''.join(yes_point_list),
                   now_point=u''.join(now_point_list),
                   first_market=combination_obj.first_market, second_market=combination_obj.second_market)
        user_profit[combination_obj.user].append(message)

    for user, message_list in user_profit.items():
        if not message_list:
            continue
        user_db = UserModel.get(user)
        if user_db is None or user_db.email is None:
            continue
        user_html = u"""
            <table border="1" cellspacing="0">
            {header}
            {message}
            </table>
        """.format(header=profit_table_header, message='\n'.join(message_list))
        send_email([user_db.email, 'ouyan19880123@163.com', 'txjzw002@163.com'], header='收益报表',
                   text=None, html=user_html)


supervisor_status_header = u"""
    <tr>
    <th>主机</th>
    <th>任务</th>
    <th>状态</th>
    <th>记录时间</th>
    </tr>
"""

exception_cal_header = u"""
    <tr>
    <th>主机</th>
    <th>来源</th>
    <th>数量</th>
    </tr>
"""

exception_info_header = u"""
    <tr>
    <th>主机</th>
    <th>来源</th>
    <th>信息</th>
    </tr>
"""


@command('status')
def report_supervisor_status():
    """
    汇报supervisor状态
    :return:
    """
    session = get_dbsession()
    try:
        # shell获取到的是服务器当地时间
        begin_datetime = datetime.now() - timedelta(seconds=1800)
        utc_begin_datetime = datetime.utcnow() - timedelta(seconds=1800)
        db_list = session.query(SupervisorStatusModel).\
            filter(SupervisorStatusModel.log_time > begin_datetime).all()
        message_list = list()
        for db in db_list:
            status_parts = db.info.split('\n')
            parts_len = len(status_parts)
            for index, item in enumerate(status_parts):
                item_parts = item.split(' ', 1)
                if index == 0:
                    message = u"""
                        <tr>
                        <td rowspan="{rowspan}">{host}</td>
                        <td>{task}</td>
                        <td>{status}</td>
                        <td>{log_time}</td>
                        </tr>
                    """.format(host=db.host, task=item_parts[0], status=item_parts[1].strip(),
                               log_time=db.log_time.strftime('%Y-%m-%d %H:%M:%S'),
                               rowspan=parts_len)
                else:
                    message = u"""
                        <tr>
                        <td>{task}</td>
                        <td>{status}</td>
                        <td>{log_time}</td>
                        </tr>
                    """.format(task=item_parts[0], status=item_parts[1].strip(),
                               log_time=db.log_time.strftime('%Y-%m-%d %H:%M:%S'))
                message_list.append(message)
        # 异常，异常记录的是UTC时间
        db_list = session.query(ExceptionInfoModel). \
            filter(ExceptionInfoModel.log_time > utc_begin_datetime).all()
        cal_dict = dict()
        exception_cal_message_list = list()
        exception_message_list = list()
        for db in db_list:
            if db.host not in cal_dict:
                cal_dict[db.host] = dict()
            if db.source not in cal_dict[db.host]:
                cal_dict[db.host][db.source] = 1
            else:
                cal_dict[db.host][db.source] += 1
            message = u"""
                <tr>
                <td>{host}</td>
                <td>{source}</td>
                <td>{info}</td>
                </tr>
            """.format(host=db.host, source=db.source, info=db.message)
            exception_message_list.append(message)
        for host, host_cal in cal_dict.items():
            for source, count in host_cal.items():
                message = u"""
                    <tr>
                    <td>{host}</td>
                    <td>{source}</td>
                    <td>{count}</td>
                    </tr>
                    """.format(host=host, source=source, count=count)
                exception_cal_message_list.append(message)
        user_html = u"""
            <h2>运行状态</h2>
            <table border="1" cellspacing="0">
            {header}
            {message}
            </table>
            <h2>异常统计</h2>
            <table border="1" cellspacing="0">
            {exception_cal_header}
            {exception_cal_message}
            </table>
             <h2>异常信息</h2>
            <table border="1" cellspacing="0">
            {exception_info_header}
            {exception_info_message}
            </table>
        """.format(header=supervisor_status_header, message='\n'.join(message_list),
                   exception_cal_header=exception_cal_header,
                   exception_cal_message='\n'.join(exception_cal_message_list),
                   exception_info_header=exception_info_header,
                   exception_info_message='\n'.join(exception_message_list))
        send_email(['txjzw002@163.com'], header='运行状态报表', text=None, html=user_html)
    except:
        session.rollback()
        print(traceback.format_exc())
        raise


if __name__ == '__main__':
    Run()
    # report_profit()
    # user_html = """
    # <table border="1" cellspacing="0">
    #
    # <tr>
    # <th>组合</th>
    # <th>起始币量</th>
    # <th>昨日币量</th>
    # <th>今日币量</th>
    # <th>收益</th>
    # <th>收益率</th>
    # </tr>
    #
    #
    #     <tr>
    #     <td>knc btc</td>
    #     <td>btc:1.0391158073</br>knc:6058.1714362314</td>
    #     <td>btc:1.0420384473</br>knc:6122.5124159727</td>
    #     <td>btc:1.0440318473</br>knc:6131.1718103530</td>
    #     <td>当日:0.0023523630</br>总体:0.0142438622</td>
    #     <td>当日:0.124%</br>总体:0.707%</td>
    #     </tr>
    #
    #         </table>
    # """
    # send_email(['txjzw002@163.com'], header='测试一下程序结果', text=None, html=user_html)
