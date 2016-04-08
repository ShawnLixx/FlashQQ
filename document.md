#Smart QQ API for python
#####基于webqq协议的api，支持接收、发送消息，获取好友信息、列表。
>####该协议中出现的uin、gid、did均为获取的号码，并不代表qq号码。

####下列函数于变量均在webQQ类下
##**基本变量：**

变量名|说明
-----|----
self.session|requests.Session()对象，为整个过程主要会话
self.msg_id|发送消息时的参数，并无特别用处，大一点就行
self.t|发送消息时的参数，腾讯并不检查数值
self.*Url|各种请求的Url

##**基本函数**

函数名|说明
-----|----
hash(b, j)|哈希算法，一些传递的参数用此加密
getQrcode()|获取二维码，扫码登陆
isLoginIn()|检查用户是否扫码二维码并登陆
getImportInfo()|在用户扫码二维码后调用该函数才能成功登入
getFriendsList()|获得好友列表
getGroupList()|获得群列表
getDiscussList()|获得讨论组列表
getMessages()|向服务器请求获取新消息
sendMsgFriend(toUin, content)|发送消息至好友
sendMsgGroup(toGid, content)|发送消息至群
sendMsgDiscuss(toDid, content)|发送消息至讨论组
getOnlinInfo()|获得好友在线状态
getRecentList()|获得最近联系人列表
getQQNumber(uin)|通过uin获取qq号
getFriendInfo(uin)|通过uin获取好友详细信息
getSelfInfo()|获取自己个人详细信息
getGroupInfo(code)|获取群详细信息
getDiscussInfo(did)|获取讨论组详细信息

##**函数详细说明**
###getQrcode()

用途|获取二维码，扫码登陆
----|--------
**参数**|**无**

返回值|说明
-----|----
qrcodeImg|Image类，二维码图片png格式

###isLoginIn()

用途|检查用户是否扫码二维码并登陆
----|---------
**参数**|**无**

返回值|说明
-----|----
1|登陆成功
2|用户已扫码，但还未在手机上点击登陆
3|二维码未失效，但用户还未扫码
4|二维码已失效
5|HTTP ERROR

###getImportInfo()

用途|在用户扫码二维码后调用该函数才能成功登入
----|--------
**参数**|**无**

返回值|说明
-----|----
1|登陆成功

###getFriendsList()

用途|获得好友列表
----|--------
**参数**|**无**

返回值|说明
-----|----
friends|一个dict，包含好友列表
0|获取失败

    friends = {
        "123456789"(uin号码): {
            "nick": "昵称",
            "markname"(无备注名的无该项): "备注名",
            "vipinfo": {
                "is_vip": 0(无vip为0， 有为1),
                "vip_level": 0,
            }
        },
        ...
    }

###getGroupList()

用途|获得群列表
----|--------
**参数**|**无**

返回值|说明
-----|----
groups|一个dict，包含群列表
0|获取失败

    groups = {
        "123456789"(gid号码): {
            "name": "群名称",
            "markname"(无备注名的无该项): "群备注名",
            "code":987654321(获得群详细信息时会有用)
        },
        ...
    }

###getDiscussList()

用途|获得讨论组列表
----|--------
**参数**|**无**

返回值|说明
-----|----
discusses|一个dict，包含讨论组列表
0|获取失败

    discusses = {
        "123456789"(did号码): {
            "name": "讨论组名称"
        },
        ...
    }

###getMessages()

用途|向服务器请求获取新消息
----|--------
**参数**|**无**

返回值|说明
-----|----
messages|一个list，包含收到的（多个）信息
0|获取失败
1|没有新消息

    messages = [
        {
            "uin": 123456789(给你发消息好友的uin),
            "type": "friend"(有"friend", "group", "discuss"三种)
            "font":  {
                "color": "000000",
                "name": "微软雅黑",
                "size": 10,
                "style": [0, 0, 0]
            }
            "time": 123456789(Unix时间)
            "content": "hello"(信息内容，有表情以[face,12]的形式插在中间)
        }
    ]

###sendMsgFriend(toUin, content)

用途|发送消息至好友
----|--------
**参数**|**toUin, content**

返回值|说明
-----|----
0|发送失败
1|发送成功

**注意，content的为str，是list形式的字符串，而不是list**
**我们之后会改进，让发送消息更加简单**

    "content" = [
        "hello"(信息内容),
        [
            "font"(固定的),
            {
                "name": "微软雅黑",
                "size": 10,
                "color": "000000",
                "style": [0, 0, 0]
            }
        ]
    ]

###sendMsgGroup(toGid, content)

用途|发送消息至群
----|--------
**参数**|**toGid, content**

返回值|说明
-----|----
0|发送失败
1|发送成功

>**content的格式跟sendMsgFriend函数参数中content相同**

###sendMsgDiscuss(toDid, content)

用途|发送消息至讨论组
----|--------
**参数**|**toDid, content**

返回值|说明
-----|----
0|发送失败
1|发送成功

>**content的格式跟sendMsgFriend函数参数中content相同**

###getOnlinInfo()

用途|获得好友在线状态
----|--------
**参数**|**无**

返回值|说明
-----|----
isOnline|一个dict，包含好友在线状态，只有在线的好友会在dict中有
0|获取失败

    isOnline = {
        "123456789"(uin号码): {
            "status": "online"(有"online", "busy", "away", "slient")
            "client_type": 1(1代表电脑，2代表手机wifi，7代表手机4G)
            }
        },
        ...
    }

###getRecentList()

用途|获得最近联系人列表
----|--------
**参数**|**无**

返回值|说明
-----|----
recentList|一个list，包含最近联系人信息
0|获取失败

    recentList = [
        {
            "type": 0(0为好友会话，1为群会话，2为讨论组会话),
            "uin": 123456789(好友会话时为uin，群会话对应gid，讨论组会话对应did),
        }
    ]

###getQQNumber(uin)

用途|通过uin获取qq号
----|--------
**参数**|**uin**

返回值|说明
-----|----
number|一个number,qq号
0|获取失败

###getFriendInfo(uin)

用途|通过uin获取好友详细信息
----|--------
**参数**|**uin**

返回值|说明
-----|----
result|一个dict，包含好友信息
0|获取失败

    result = {
        "birthday": {
            "year": 1997,
            "month": 5,
            "day": 6
        },
        "country": "国籍",
        "province": "省份",
        "city": "城市",
        "college": "大学",
        "email": "邮箱",
        "gender": "male"(or "female"),
        "homepage": "主页",
        "phone": 手机号,
        "mobile": 也是手机号,
        "uin": 123456789,
        "shengxiao": 1(生肖，1-12),
        "vip_info": 0,
    }

###getSelfInfo()

用途|获取自己个人详细信息
----|--------
**参数**|**无**

返回值|说明
-----|----
result|一个dict，包含自己信息
0|获取失败

>**result格式跟getFriendInfo返回值中content格式相同**

###getGroupInfo(code)

用途|获取群详细信息
----|--------
**参数**|**code(注意不是gid，是获得群列表里获得的code)**

返回值|说明
-----|----
groupInfo|一个dict，包含群详细信息
0|获取失败

    groupInfo = {
        "name": "群名称",
        "markname": "群备注名"
        "memo": "群公告",
        "class": 班级,
        "gid":123456789(群的gid),
        "code": 123456789(群的code),
        "createtime": 123456789(群创建的UNIX时间),
        "level": 0(群等级),
        "owner": 123456789(创建者的uin),
        "members": {
            "123456789"(群成员的uin): {
                "nick": "昵称",
                "country": "国籍"
                "province": "省份",
                "city": "城市",
                "gender": "male"(男或女),
                "client_type": 1(同获取好友在线状态里的client_type),
                "groupCard": "该用户的群名片",
                "is_vip": 0(是否vip),
                "vip_level": 0(vip等级),
            }
        }
    }

###getDiscussInfo(did)

用途|获取讨论组详细信息
----|--------
**参数**|**did(获得讨论组列表里获得的did)**

返回值|说明
-----|----
discussInfo|一个dict，包含讨论组详细信息
0|获取失败

    discussInfo = {
        "name": "讨论组名称",
        "members": {
            "123456789"(讨论组成员的uin): {
                "nick": "昵称",
                "client_type": 1(同获取好友在线状态里的client_type),
            }
        }
    }