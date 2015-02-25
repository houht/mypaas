
cattle安装文档

***
第一章、系统配置

1.1 网络配置  
建立br0内容如下:  
DEVICE="br0"  
BOOTPROTO="static"  
ONBOOT="yes"  
IPADDR=192.168.1.2  
NETMASK=255.255.255.0  
TYPE=Bridge  
GATEWAY=10.16.123.254  


第二章、kvm与libvirt安装

2.1 检测服务器是否支持kvm  
    egrep '(vmx|svm)' --color=always /proc/cpuinfo  
    若输出内容不为空，则服务器支持kvm虚拟化  
2.2 安装  
   yum install -y kvm kmod-kvm kvm-qemu-img libvirt libvirt-devel Python-virtinst virt-manager virt-viewer bridge-utils  
2.3 重新启动系统  
     reboot  

第三章、安装libguestfs  

3.1 安装  
   yum install -y libguestfs libguestfs-tools libguestfs-tools-c python-libguestfs libguestfs-winsupport  

第四章、安装lvm2  

4.1 确认是否已经安装lvm2  
   rpm -qa|grep lvm2  
   输出如下信息表示已经安装，本章不用在安装。  
   lvm2-2.02.98-9.el6_4.3.x86_64  
   lvm2-libs-2.02.98-9.el6_4.3.x86_64  
4.2 安装lvm2  
    yum install -y lvm2 lvm2-libs  

第五章、安装ntfs-3g和ntfsprogs  

5.1 下载安装文件  
  export http_proxy=http://user:passwd@ip:port 设置代理，此步可以不要  
  wget http://tuxera.com/opensource/ntfs-3g_ntfsprogs-2014.2.15.tgz  
5.2 安装gcc，此步可略  
  yum install -y gcc  
5.3 安装ntfs-3g_ntfsprogs  
  tar zxvf ntfs-3g_ntfsprogs-2014.2.15.tgz  
  cd ntfs-3g_ntfsprogs-2014.2.15  
  ./configure  
  make  
  make install  

  说明：在configure时出现如下告警，不影响安装。  
  /bin/rm: cannot remove `libtoolT': No such file or directory  

第六章、mq消息处理器安装  

6.1 amqp安装  
  tar zxvf amqp-1.4.5.tar.gz  
  cd  amqp-1.4.5  
  python setup.py build  
  python setup.py install  
6.2 kombu安装  
  tar zxvf ordereddict-1.1.tar.gz  
  cd ordereddict-1.1  
  python setup.py build  
  python setup.py install  
  
  tar zxvf importlib-1.0.3.tar.gz  
  cd importlib-1.0.3  
  python setup.py build  
  python setup.py install  
  
  tar zxvf anyjson-0.3.3.tar.gz  
  cd anyjson-0.3.3  
  python setup.py build  
  python setup.py install  
  
  tar zxvf kombu-3.0.15.tar.gz  
  cd kombu-3.0.15
  python setup.py build  
  python setup.py install  
6.3安装yaml  

   tar  zxvf PyYAML-3.11.tar.gz  
   cd PyYAML-3.11  
   python setup.py  install   

第七章、dhcp安装  

7.1 安装dhcp  
yum -y install dhcp  

第八章、安装cattle  

8.1 安装cattle  
1）、进入/usr/lib/python2.6/site-packages目录  
2）、上传cattle-2015-01.tar.gz并解压  
3）、上传cattle.conf，businessAction.conf 到"/etc/"目录，并修改响应配置  
4）、根据配置文件建立相关目录：  
vm 目录    ： mkdir -p /data/vm/  
存储目录   ： mkdir -p /data/storage/  
模板目录   ： mkdir -p /data/images/  
5）、配置相关属性  
MQ地址              ： mq_addr  
应用服务器地址   ： ip_addr   
模板下载地址      ： download_addr  
网桥                    ： bridge  
vg名字                ： vg_name  
等等其他相关配置  
6）、dhcp配置  
配置/etc/dhcpd.conf  
/usr/sbin/dhcpd为启动程序  
/var/lib/dhcpd/dhcpd.leases 为租约记录文件  
/etc/sysconfig/dhcpd 配置dhcp在特定网口上提供服务DHCPDARGS=bro 多个网口使用空格分开  


需要修改，例如：  
subnet 192.168.2.0 netmask 255.255.255.0 {  
option routers 192.168.2.1;  
option time-offset -18000;  
option broadcast-address 255.255.255.254;  
max-lease-time 43200;  
default-lease-time 21600;  
option subnet-mask 255.255.255.0;  
option domain-name-servers 114.114.114.114;  
  
}  

subnet 192.168.122.0 netmask 255.255.255.0 {  
  
}  

subnet 10.16.123.0 netmask 255.255.255.0 {  
  
}  


进入”/etc/dhcp“目录，上传dhcpd.conf文件，并做相应的修改  
7）、新建/etc/cattle/script目录，并上传服务配置文件  

mkdir  -p /etc/cattle/script   
8）、上传应用到的数据库到“/etc/”目录  

9）、新建/etc/koala目录，上传koala.conf文件，并修改文件当中的数据库连接地址，消息配置，模板下载配置等  
mkdir -p /etc/koala  


8.2 安装cattle_monitor  

8.3 搭建rabbitMQ消息队列  

-----------------------------------
3、python组件  

1)、django1.6.8  

tar  zxvf Django-1.6.8.tar.gz   
cd Django-1.6.8  
python setup.py  install  

2)、rest_framework  

tar  zxvf djangorestframework-3.0.0.tar.gz   
cd djangorestframework-3.0.0  
python setup.py  install  

3)、mysql  
yum install mysql-server mysql-libs mysql  
service mysqld start  
mysqladmin -u root password "123456"   
service mysqld restart
进入数据库：mysql -uroot -p123456，创建数据库：create database koala;  
4）、MySQLdb  

需要
yum install -y  python-devel  
yum install -y  mysql-devel    

tar  zxvf MySQL-python-1.2.3.tar.gz  
cd MySQL-python-1.2.3  
python setup.py install  

8.3 安装Koala  
1）、进入Koala/Koala目录，修改settings.py文件的数据库链接地址  
2）、Koala目录，执行python manage.py syncdb，执行的时候创建管理员用户和密码  
3）、修改app_serviceinfo表，添加镜像文件  
例如：iis2003	1	iis2003	normal	http  
4）、修改vm_image表，添加镜像，例如  
1	0F7620DDF32543A097372F11C5B8877F	 0	 kvm  
5）、镜像上传到网盘或者拷贝到指定目录，例如：  
scp wintest03 root@10.16.123.81:/data/images/  
scp 0F7620DDF32543A097372F11C5B8877F root@10.16.123.81:/data/images/  

8.4 测试  
1）、首先进入/usr/lib/python2.6/site-packages/cattle目录，执行python cattled.py start，启动cattle  
2）、然后进入/usr/lib/python2.6/site-packages/Koala目录，执行python manage.py runserver 0.0.0.0:9000，启动restful接口  
3）、进入/usr/lib/python2.6/site-packages/koala_task目录，执行python koala_task_server.py ，启动后台任务以及监控  
4）、访问http://10.16.123.81:9000/v1/vm/ 与http://10.16.123.81:9000/v1/app/进行测试。  

测试部分json如下：  
1，应用创建  
{   
"action":"create",   
"taskId":"E111111122222222001",   
  
"command":{   
"serviceId": "iis2003",   
"appName":"iis_test",   
"mem":1024,   
"disk": 500 ,   
"cpu":1,   
"appFileId":"eeeeeeeeeee",   
"appEnv":"",   
"domain":"www.abc.com",   
"unit":1   
}   
}   

2，应用更新，暂无  

{   
"action":"update",   
"taskId":"E1111111222222225",   
  
"command":{   
  
"mem":1024,   
"disk": 500 ,   
"cpu":1,   
"appFileId":"111111111",   
"appEnv":"",   
"domain":"www.abc.com",   
}   
}   

3，应用启动关闭删除  
{   
"action":"start/stop/drop",   
"taskId":"E1111111222222225",   
  
"command":{   
"appId": "acdb1e62898711e4929afe5400e41488"   
}   
}   
  


4，vm创建  
{   
"action":"create",   
"taskId":"E111111122222222001",   
"command":{   
"vmAlias":"test_kvm_001",   
"cpu":2,   
"mem":1024,   
"size": 800,   
"attachDisks":[{ "hardpoints":"vdb","size":500}],   
"imageId":"0F7620DDF32543A097372F11C5B8877F"   
}   
}  


5，vm启动关闭删除
{   
"action":"start/destroy/drop",   
"taskId":"E111111122222222115",   
  
"command":{   
"vmId": "ca09caa68ff411e4b80efe5400e41488"   
}   
}   


5，vm代理设置  

{    
"action":"proxy",   
"taskId":"E111111122222222115",   
  
"command":{   
"vmId": "ca09caa68ff411e4b80efe5400e41488",   
"type": "tcp",   
"port": 8081   
}   
}   



##########################################   
相关状态  

creating created createFail   

starting running startFail   

stopping stopFail stoped   

dropping destroyed dropFail   



############################################  
日志目录  
cattle日志 /var/log/cattle  
koala_task日志 /var/log/koala/  
cattle_monitor日志  /var/log/cattle  
Koala日志，路由配置  





