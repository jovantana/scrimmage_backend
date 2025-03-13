from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from .service import *
from .utils import *
from app.models import Article, db


newsfeed_bp = Blueprint('newsfeed', __name__, url_prefix='/newsfeed')


@newsfeed_bp.route('/article/<article_id>')
def get_article(article_id):
    """Endpoint to retrieve a single article by id"""
    try:
        article = Article.query.filter(Article.article_id==article_id).first()        
        
        if article:
            art_json = article.as_dict()
            response = {'data': art_json}
            status = 200
        else:
            response = "Article not found"
            status = 404

        return response, status
    except Exception as e: 
        return f"Error getting article: {e}", 400


@newsfeed_bp.route('/articles')
def get_all_articles():
    """Endpoint to retrieve all articles"""
    try:
        tags = request.args.getlist('tags')

        if tags:
            articles = Article.query.filter(
                Article.tags.overlap([tags])
            )
        else:
            articles = Article.query.order_by(desc(Article.timestamp)).limit(200)

        art_json = [art.as_dict() for art in articles]

        if art_json:
            response = {'data': art_json}
            status = 200
        else:
            response = "No data available"
            status = 404
        
        return response, status

    except Exception as e: 
        return f"Error getting articles: {e}", 400
