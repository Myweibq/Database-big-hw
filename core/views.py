from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
from django.shortcuts import redirect, get_object_or_404
from uuid import UUID  # 确保导入UUID模块，否则会报错；  ps：后来也没用到，但是还是保留了

from .models import Profile, Post, LikePost, FollowersCount

# # 旧版本的函数，已经废弃
# # 主页，显示正在关注的人的帖子；但是不能显示自己的贴子
# @login_required(login_url='signin')
# def index(request):
#     # 获取当前活跃用户的基本信息
#     user_object = User.objects.get(username=request.user.username)
#     user_profile = Profile.objects.get(user=user_object)

#     user_following_list = []
#     # 筛选出该用户的正在关注的人
#     user_following = FollowersCount.objects.filter(follower=request.user.username)
#     for users in user_following:
#         user_following_list.append(users.user)
#     # 筛选出所有正在关注的人的所有帖子
#     post = []
#     for usernames in user_following_list:
#         feed_lists = Post.objects.filter(user=usernames)
#         post.append(feed_lists)

#     post_list = list(chain(*post))

#     # 筛选出所有的可以关注的人
#     all_users = User.objects.all()

#     # #筛选出所有正在关注的人
#     user_following_all = []
#     for user in user_following:
#         user_list = User.objects.get(username=user.user)
#         user_following_all.append(user_list)
#     # #除掉已经关注的人
#     new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
#     # 除掉自己
#     current_user = User.objects.filter(username=request.user.username)
#     final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]

#     # 打乱顺序
#     random.shuffle(final_suggestions_list)

#     # 获取最终列表用户的个人信息
#     # #获取id
#     username_profile = []
#     username_profile_list = []
#     for users in final_suggestions_list:  # final_suggestions_list:
#         username_profile.append(users.id)
#     # #获取信息
#     for ids in username_profile:
#         profile_lists = Profile.objects.filter(id_user=ids)
#         username_profile_list.append(profile_lists)

#     suggestions_username_profile_list = list(chain(*username_profile_list))
#     return render(request, 'index.html', {'user_profile': user_profile, 'posts': post_list,
#                                           'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def index(request):
    # 获取当前活跃用户的基本信息
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # 筛选出该用户的正在关注的人
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    user_following_list = [users.user for users in user_following]

    # 获取当前用户的帖子
    user_posts = Post.objects.filter(user=request.user.username)

    # 筛选出所有正在关注的人的所有帖子
    following_posts = []
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        following_posts.append(feed_lists)

    # 合并当前用户的帖子和关注的人的帖子，并确保没有重复项
    post_list = list(chain(user_posts, *following_posts))
    post_list = list(dict.fromkeys(post_list))  # 移除可能的重复项

    # 按照创建时间降序排列帖子
    post_list.sort(key=lambda x: x.created_at, reverse=True)

    # 筛选出所有的可以关注的人
    all_users = User.objects.all()

    # 筛选出所有正在关注的人
    user_following_all = [User.objects.get(username=user.user) for user in user_following]
    
    # 除掉已经关注的人和自己
    new_suggestions_list = [x for x in all_users if x not in user_following_all and x != request.user]

    # 打乱顺序
    random.shuffle(new_suggestions_list)

    # 获取最终列表用户的个人信息
    username_profile_list = Profile.objects.filter(id_user__in=[user.id for user in new_suggestions_list])

    suggestions_username_profile_list = list(username_profile_list)
    
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': post_list,
                                          'suggestions_username_profile_list': suggestions_username_profile_list[:4]})
# 登录
def signin(request):
    # 如果是post请求
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # 校验
        user = auth.authenticate(username=username, password=password)
        # 如果用户存在
        if user is not None:
            # messages.info(request, '登录成功')
            # return redirect('signin')
            auth.login(request, user)
            return redirect('/')
        # 如果用户不存在
        else:
            messages.info(request, '登录失败')
            return redirect('signin')
    # 如果不是post请求
    else:
        return render(request, 'signin.html')


# 注册
def signup(request):
    # 如果是post请求
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['username'] # 默认username为firstname，因为first_name和last_name字段没有在注册页面显示，且在该版本Django中IS NOT NULL约束
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        lastname = request.POST['password']  # 把密码设置为lastname，方便数据库管理查看密码，因为hashed密码无法查看(sha256加密)
        # 如果密码相等
        if password == password2:
            # 如果邮箱已存在
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect('signup')
            # 如果用户名已经存在
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect('signup')
            # 如果都不存在
            else:
                user = User.objects.create_user(username=username, first_name = firstname, last_name = lastname, email=email, password=password)
                user.save()

                # 登录
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
        
                # 设置默认的个人信息
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, bio='这个人很懒，什么都没写', location='这个人很懒，什么都没写')
                new_profile.save()
                # 跳转到设置个人信息界面
                return redirect('settings')
        # 如果密码不等，提示
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    # 如果请求不是post，保持在注册界面
    else:
        return render(request, 'signup.html')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if not request.FILES.get('image'):
            user_profile.bio = request.POST['bio']
            user_profile.location = request.POST['location']
            user_profile.save()

        if request.FILES.get('image'):
            user_profile.profileimg = request.FILES.get('image')
            user_profile.bio = request.POST['bio']
            user_profile.location = request.POST['location']
            user_profile.save()
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        # 模糊查询 忽略大小写 icontains
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        # 搜索到的人的基本信息列表
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html',
                  {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def profile(request, pk):
    # 用户对象
    user_object = User.objects.get(username=pk)
    # 用户基本信息
    user_profile = Profile.objects.get(user=user_object)
    # 用户帖子
    user_posts = Post.objects.filter(user=pk)
    # 用户帖子数
    user_post_length = len(user_posts)

    # 当前用户
    follower = request.user.username
    # 查询的用户
    user = pk
    # 如果有查到的，说明已经关注过，只能进行取消关注操作
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = '已关注'
    # 反之同理
    else:
        button_text = '关注'

    # 查询查询的用户的关注者，跟随者
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        # 操作者，当前用户
        follower = request.POST['follower']
        # 查看的人
        user = request.POST['user']

        # 删除一条数据
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        # 新增一条数据
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    # 被这个用户喜欢 +1
    if not like_filter:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    # 没有被这个用户喜欢 -1
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

def about(request):
    return render(request, 'about.html')

def nodelete(request):
    return render(request, 'nodelete.html') # 没实现删除动态的时候无聊编写的

# 实现删除帖子，遇到好多bug
# 目前逻辑是，如果当前用户是帖子的作者，则可以删除帖子；否则不出现删除的按钮
@login_required(login_url='signin')
def delete_post(request, post_id):
    # 获取帖子对象或返回404错误页面如果不存在
    try:
        post = get_object_or_404(Post, id=post_id)

        # 检查当前用户是否是帖子的作者
        if request.user.username == post.user:  # 如果user字段是CharField
            post.delete()
            messages.success(request, '您的帖子已成功删除.')
        else:
            messages.error(request, '您只能删除自己的帖子.')

    except Exception as e:
        # 记录异常信息，便于调试
        messages.error(request, f'发生错误: {str(e)}')

    return redirect('index')  # 假设你的主页URL名称为'index'