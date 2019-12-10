from django.shortcuts import render
from system import form
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from .models import Project,Job
from .models import MyUser as User
from django.db.models import Q
from audit.loginRequiredMixin import LoginRequiredMixin
# Create your views here.
from django.shortcuts import redirect
import datetime
# 登录接口
class AuthLogin(View):
    # 跳转登录页面
    def get(self,request):
        login_form = form.UserForm()

        return render(request,'login.html',locals())
    def post(self,request):
        # 获取form表单内容
        login_form = form.UserForm(request.POST)
        message = "请检查填写的内容！"
        # 校验内容
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                # 验证账户密码是否争取
                user = auth.authenticate(username=username, password=password)
                # 判断是否验证成功
                if user is not None:
                    # 记录session
                    auth.login(request, user)
                    # 判断是否管理员
                    if user.root:

                        try:
                            # 获取一个项目，跳转页面到管理员页面
                            project =Project.objects.first().id
                            return redirect('/adminprojectlist?projectId='+str(project))
                        except:
                            return redirect('/adminprojectlist/')

                    else:
                        # 跳转到普通员工界面
                        return redirect('/index/')


                else:

                    message = "密码不正确！"
            except:
                message = "用户不存在或密码不存在！"
        login_form = form.UserForm()

        return render(request, 'login.html', locals())


# 注册页面
class RegisterView(View):


    def get(self,request):
        register_form = form.RegisterForm()
        return render(request,'register.html',locals())
    #添加用户
    def post(self,request):
        #判断是否为管理员用户，如果是则可以添加用户

        register_form = form.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            root = request.POST.get('root')
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(username=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())

                # 当一切都OK的情况下，创建新用户

                user = User.objects.create_user(username, email, password1)
                # 管理员权限确定
                if root == 'on':
                    root = True
                if root == None:
                    root = False
                user.root = root
                user.save()
                return redirect('/login/')
        register_form = form.RegisterForm()

        return render(request, 'register.html', locals())





#退出接口
class LoginOut(View):
    def get(self,reqeust):
        auth.logout(reqeust)
        return redirect('/login/')

#发布项目操作
class pushProject(View,LoginRequiredMixin):
    def get(self,request):
        # 获取项目列表
        projectList = Project.objects.all()
        return render(request,'pushProject.html',{"projectlist":projectList})
    def post(self,request):
        # 获取session中的用户
        id = request.user.id
        # 获取项目名
        name=request.POST.get("content")
        # 创建项目
        project=Project.objects.create(name=name,pushilder=id,create_time=datetime.datetime.now())
        # 获取现有所有的普通成员
        userlist =User.objects.filter(root=False)
        # 为所有成员创建任务
        for user in userlist:
            Job.objects.create(projectId=project.id,status=0,userId=user.id)

        return redirect('/pushproject/')
#
# 普通成员列表页面
class ProjectListView(View):
    def get(self,request):
        type=request.GET.get('type',None)
        # 1为已提交项目名，2为已评分项目，0为未提交

        if type=='1':
            joblist =Job.objects.filter(Q(status=1)&Q(userId=request.user.id))
        elif type=='2':
            joblist=Job.objects.filter(Q(status=2)&Q(userId=request.user.id))
        else:
            joblist=Job.objects.filter(Q(status=0)&Q(userId=request.user.id))
            type = '0'

        #
        joblist2=[]
        for job in joblist:
            jobdict={}
            # 获取项目名
            name=Project.objects.get(id=job.projectId).name
            jobdict['name']=name
            # 如果未评分则填写未打分
            if job.grade!=None:
                jobdict['grade']=job.grade
            else:
                jobdict['grade']='未打分'
            jobdict['meaching_grade']=job.meaching_grade
            if jobdict['meaching_grade']==None:
                jobdict['meaching_grade']='未打分'

            jobdict['id']=job.id

            joblist2.append(jobdict)

        return render(request,'projectlist.html',{"joblist2":joblist2,"status":int(type)})
# 提交任务
class AddJobView(View):
    def get(self,request):
        # 获取任务id
        id =request.GET.get("id")
        # 获取任务
        job=Job.objects.get(id=id)
        # 获取项目名
        name = Project.objects.get(id=job.projectId).name
        return render(request,'addjob.html',locals())

    def post(self,request):
        # 获取内容
        content=request.POST.get("content")
        # 获取任务id
        id=request.POST.get("id")
        #  查找任务，并更新任务内容和状态，status 1为已提交
        job=Job.objects.get(id=id)
        job.content=content
        job.status=1
        # job.create_time(datetime.datetime.now())
        job.save()
        return redirect('/index/')
# 编辑任务
class EditJobView(View):
    def get(self,request):
        id = request.GET.get("id") # 获取任务id

        job = Job.objects.get(id=id)#  查找任务，
        # 项目信息
        project=Project.objects.get(id=job.projectId)
        return render(request, 'editjob.html', locals())

    def post(self,request):
        # 获取内容
        content = request.POST.get("content")
        # 获取任务id，并进行更新保存
        id = request.POST.get("id")
        job = Job.objects.get(id=id)
        job.content = content
        job.status = 1

        job.save()
        return redirect('/index?type=1')
# 评分页面
class ScoreJobView(View):
    def get(self,request):
        # 获取任务id
        id = request.GET.get("id")
        # 获取任务信息
        job = Job.objects.get(id=id)
        # 获取项目信息
        project = Project.objects.get(id=job.projectId)
        # 获取用户信息
        user=User.objects.get(id=job.userId)

        return render(request, 'scoreJob.html', locals())

    def post(self,request):
        # 获取前端获取的信息并提交保存
        id =request.POST.get("id")
        score=request.POST.get("score")
        job=Job.objects.get(id=id)
        job.status=2
        job.grade=score
        job.save()
        project =Project.objects.get(id=job.projectId)
        return redirect('/adminprojectlist?type=0&projectId='+str(project.id))
# 管理员页面
# 操作跟普通用户一样，做了一系列的查询操作，拼接出需要的字段
class AdminProjectListView(View):

    def get(self,request):
        # 获取项目id，获取类型1为已评分，0为未评分
        projectId=request.GET.get("projectId",None)

        type=request.GET.get("type",None)
        # 获取项目列表
        projectList=Project.objects.all()


        if type is not None and int(type)==1:
            # 获取任务列表
            JobList = Job.objects.filter(status=2).filter(projectId=projectId)
            # 遍历填写相应信息
            joblist2 = []
            for job in JobList:
                jobdict = {}
                username = User.objects.get(id=job.userId).username

                jobdict['user'] = username
                jobdict['id']=job.id

                jobdict['meaching_grade'] = job.meaching_grade
                if jobdict['meaching_grade'] is None:
                    jobdict['meaching_grade']='未打分'
                jobdict['grade']=job.grade
                if jobdict['grade'] is None:
                    jobdict['grade']='未打分'
                joblist2.append(jobdict)
                type=1


        else:
            if projectId is not None:

                JobList = Job.objects.filter(status=1).filter(projectId=projectId)
            else:
                JobList=[]

            joblist2=[]
            for job in JobList:
                jobdict={}
              
                username=User.objects.get(id=job.userId).username
          
                jobdict['user']=username
                jobdict['id']=job.id
                if job.meaching_grade==None:
                    jobdict['meaching_grade']='未打分'
                else:

                    jobdict['meaching_grade']=job.meaching_grade

                joblist2.append(jobdict)
            type = 0
        if projectId is not None:
            name=Project.objects.get(id=projectId).name
        else:
            name='暂无'
        userlist =User.objects.filter(root=False)

        return render(request,'adminProjectList.html',{"status":type,"joblist":joblist2,"projectlist":projectList,'name':name,"userlist":userlist,'projectId':projectId})

    def post(self,request):

        projectId = request.POST.get("projectId", None)
        usserId = request.POST.get("userId", None)

        graderank = request.POST.get("graderanke", None)#分数段
        projectList2=Project.objects.all()

        global type

        # 判断是查询评分的还是

        if graderank is not None:
            JobList = Job.objects.filter(status=2)
            # 切分最大分数和最小分数
            min, max= graderank.split("-")
            # 进行大于和小于查询
            joblist=JobList.filter(Q(grade__gt=int(min)) & Q(grade__lte=int(max)))


            joblist2 = []
            for job in joblist:
                jobdict = {}
                username = User.objects.get(id=job.userId).username

                jobdict['user'] = username
                if job.meaching_grade == None:
                    jobdict['meaching_grade'] = '未打分'
                else:

                    jobdict['meaching_grade'] = job.meaching_grade
                jobdict['grade'] = job.grade
                joblist2.append(jobdict)
                type=1



        else:

            JobList = Job.objects.filter(status=1)

            if projectId is not None:
                JobList=JobList.filter(projectId=projectId)
            if usserId is not None:
                JobList=JobList.filter(userId=usserId)
            joblist2 = []
            for job in JobList:
                jobdict = {}

                username = User.objects.get(id=job.userId).username

                jobdict['user'] = username


                jobdict['id']=job.id
                if job.meaching_grade==None:
                    jobdict['meaching_grade']='未打分'
                else:

                    jobdict['meaching_grade']=job.meaching_grade


                joblist2.append(jobdict)
            type = 0


        name=Project.objects.get(id=projectId).name
        userlist =User.objects.filter(root=False)


        return render(request, 'adminProjectList.html',
                      {"status": type, "joblist": joblist2, "projectlist": projectList2, 'name': name,
                       "userlist": userlist, 'projectId': projectId})













