from tkinter import N
from django.db import models

# Create your models here.
class UserInput(models.Model):
    youtube_video_id = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.youtube_video_id
    
    def list_data(self):
        return [self.youtube_video_id, self.created_at]
    
class VideoMeta(models.Model):
    youtube_video_id = models.CharField(max_length=15, unique=True)
    title = models.TextField(null=True)
    desc = models.TextField(null=True)
    tags = models.TextField(null=True)
    duration = models.FloatField(null=True)
    age_limit = models.IntegerField(null=True)
    view_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    view_like_ratio_smoothed = models.FloatField(null=True)
    is_comments_enabled = models.BooleanField(null=True)
    is_live_content = models.BooleanField(null=True)
    cat_codes = models.IntegerField(null=True)
    desc_neu = models.FloatField(null=True)
    desc_neg = models.FloatField(null=True)
    desc_pos = models.FloatField(null=True)
    desc_compound = models.FloatField(null=True)
    comments_neu = models.FloatField(null=True)
    comments_neg = models.FloatField(null=True)
    comments_pos = models.FloatField(null=True)
    comments_compound = models.FloatField(null=True)
    votes = models.FloatField(null=True)
    no_comments_binary = models.BooleanField(null=True)
    model_prediction = models.CharField(max_length=8, null=True)
    comment_count = models.IntegerField(null=True)
    date_published = models.CharField(max_length=30)
    channel_name = models.CharField(max_length=50)
    channel_id = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.youtube_video_id
    
    def list_data(self):
        return [self.youtube_video_id, self.title, self.desc, self.tags, self.duration, 
                self.age_limit, self.view_count, self.like_count, self.view_like_ratio_smoothed, 
                self.is_comments_enabled, self.is_live_content, self.cat_codes, self.desc_neu, 
                self.desc_neg, self.desc_pos, self.desc_compound, self.comments_neu, self.comments_neg, 
                self.comments_pos, self.comments_compound, self.votes, self.no_comments_binary, 
                self.model_prediction, self.comment_count, self.date_published, self.channel_name, self.channel_id, 
                self.created_at, self.updated_at]

class Comments(models.Model):
    youtube_video_id = models.CharField(max_length=15)
    cid = models.CharField(max_length=50)
    text = models.TextField()
    time = models.CharField(max_length=20)
    author = models.TextField()
    channel = models.CharField(max_length=50)
    votes = models.CharField(max_length=10)
    heart = models.BooleanField(null=True)
    
    def __str__(self):
        return self.youtube_video_id
    
    def list_data(self):
        return [self.youtube_video_id, self.cid, self.text, self.time, 
                self.author, self.channel, self.votes, self.heart]

class UserTargetSelect(models.Model):
    youtube_video_id = models.CharField(max_length=15)
    user_prediction = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.youtube_video_id
    
    def list_data(self):
        return [self.youtube_video_id, self.user_prediction, self.created_at]
    
