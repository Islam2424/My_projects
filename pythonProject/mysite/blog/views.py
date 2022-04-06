from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .forms import EmailPostForm, CommentForm, SearchForm, LoginForm, UserRegistrationForm
from haystack.query import SearchQuerySet
from .models import Post, Comment


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'post/list.html'


def post_detail(request, year, month, day, post, ):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            new_comment = False
    else:
        comment_form = CommentForm()
        return render(request, 'post/detail.html', {'post': post,
                                                    'comments': comments,
                                                    'new_comment': new_comment,
                                                    'comment_form': comment_form})
    return render(request, 'post/detail.html', {'post': post,
                                                'comments': comments,
                                                'new_comment': new_comment,
                                                'comment_form': comment_form})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "{} ({}) recommends you reading '{}'".format(cd['name'], cd['email'], post.title)
            message = "Read '{}' at {}\n\n{}\'s comments:{}".format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admi@myblog.com', [cd['to']])
            return render(request, 'post/ok.html', {'post': post, 'form': form, 'sent': sent})
    else:
        form = EmailPostForm()
        return render(request, 'post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_search(request):
    form = SearchForm()
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            results = SearchQuerySet().models(Post).filter(content=cd['query']).load_all()
            total_results = results.count()
    return render(request, 'post/search.html', {'form': form,
                                                'cd': cd,
                                                'results': results,
                                                'total_results': total_results})


@login_required
def dashboard(request):
    return render(request, 'registration/dashboard.html', {'section': dashboard})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('AUTh')
                else:
                    return HttpResponse('No Ok')
            else:
                return render(request, 'registration/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})
