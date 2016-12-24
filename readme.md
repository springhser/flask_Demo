V1.0  时间：2016-12-19
1、概述：简单的实现了一个个人博客网站的基本功能，比较粗糙(特别是前端方面)，主要参考Miguel Grinberg写的《Flask Web开发
：基于Python的web应用开发实战》，根据自身需求进行取舍和修改

2、主要实现功能：
1）前台：
（1）用户登录、注册功能。关键点：令牌的实现和利用邮箱进行认证
（2）用户的资料展示和修改。关键点：上传图片；在关注文章和评论文章两个列表涉及的一对多、多对多关系的
运用
（3）用户评论和关注。关键点：模板和分页
（4）文章分类和列表。
2）后台
（5）用户的管理。关键点：用户的评论功能的开启和关闭
（6）博客的管理（包括博客的编写）。关键点：pagedown和markdown文本的操作和存储，时间的运用
（7）博客分类的管理。
（8）评论的管理。关键点：评论的屏蔽和显示
（9）网站默认图片资源的管理（主要为修改默认用户头像和首页背景）。