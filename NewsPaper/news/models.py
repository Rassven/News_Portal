from django.db import models
from datetime import datetime
from django.contrib.auth.models import User  # ,AbstractUser, AbstractBaseUser
from django.db.models import Sum


class Author(models.Model):
    rating = models.IntegerField(default=0)  # Author_rating
    # time = models.DateTimeField(auto_now_add=True)  # ?date_joined (default=timezone.now)
    # status = models.CharField(max_length=1, choices=status_list, default='v')
    author_user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_rating(self):
        self.rating = 0
        # "суммарный" рейтинг каждой статьи автора ?==? rating
        p_rating = self.post_set.aggregate(p_r_summ=Sum('rating'))
        post_author_rating = p_rating.get('p_r_summ')
        # суммарный рейтинг всех комментариев автора
        c_rating = self.author_user.comment_set.aggregate(c_r_summ=Sum('rating'))
        comment_author_rating = c_rating.get('c_r_summ')
        # суммарный рейтинг всех комментариев К статьям автора
        p_c_rating = Comment.objects.filter(post__author_id=author_user_id).aggregate(c_r_summ=Sum('rating'))
        author_comments_rating = p_c_rating.get('c_r_summ')

        self.rating = (post_author_rating)*3 + comment_author_rating + author_comments_rating
        self.save()
        return self.rating


class Category(models.Model):
    # category_name = models.CharField(max_length=12, choices=category_list, default='None')
    category_name = models.CharField(max_length=32, unique=True)


class Post(models.Model):
    time = models.DateTimeField(auto_now_add=True)  # publication_time
    type_list = [('n', 'Новость'), ('a', 'Статья'), ]
    post_type = models.CharField(max_length=1, choices=type_list, default='a')
    # confines = models.CharField(max_length=1, choices=confines_list, default='a')
    title = models.CharField(max_length=255)  # article_title
    text = models.TextField()  # article_text
    rating = models.IntegerField(default=0)  # article_rating =likes-dislikes
    likes = models.IntegerField(default=0)  # article_likes
    dislikes = models.IntegerField(default=0)  # article_dislikes
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    category = models.ManyToManyField('Category', through='PostCategory')

    def like(self):
        # if "user" != "author"
        self.likes += 1
        self.rating = self.likes - self.dislikes
        self.save()

    def dislike(self):
        # if "user" != "author"
        self.dislikes += 1
        self.rating = self.likes - self.dislikes
        self.save()

    def preview(self):
        text_preview = f'{self.text[:124:]} ...'
        return text_preview


class PostCategory(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)


class Comment(models.Model):
    time = models.DateTimeField(auto_now_add=True)  # publication_time
    text = models.TextField(null=False)  # comment_text
    rating = models.IntegerField(default=0)  # comment_rating =likes-dislikes
    likes = models.IntegerField(default=0)  # comment_likes
    dislikes = models.IntegerField(default=0)  # comment_dislikes
    # display = models.CharField(max_length=1, choices=display_list, default='a')
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    c_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        # if "user" != "author"
        self.likes += 1
        self.rating = self.likes - self.dislikes
        self.save()

    def dislike(self):
        # if "user" != "author"
        self.dislikes += 1
        self.rating = self.likes - self.dislikes
        self.save()
