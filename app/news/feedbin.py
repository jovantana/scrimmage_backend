from datetime import datetime, timedelta
from math import ceil
from .service import *
from .utils import get_articles
from app.models import Article
from app.config import socketio
import json


def get_feedbin_entries(app, db):
    print('requesting data from feedbin...')

    with app.app_context():
        # get unread articles ids from feedbin
        response = get_unread_entries()
        if response.ok: # if we have successfully get the data we sort the ids in the var entries_ids
            entries_ids = response.json()
        else: # exit the function
            print('no data..')
            return

        if len(entries_ids)<1: # in case we have got an empty array exit the function
            return
        
        # how many articles to get from feedbin? the api support tell 100 ids at one call
        ids_card = 10 # number of articles to get from feedbin api

        times = ceil(len(entries_ids)/ids_card) # how many times should we request the data from the feedbin api
        tags = get_tags() # get all registerd tags in feedbin ! this function is temporarily we will use another way to extract tags from articles
        for ids_range in range(times):
            # we split the list of ids to chunks of ids_card
            int_ids = entries_ids[ids_range*ids_card:(ids_range+1)*ids_card]

            # create a string to use in the request to get articles
            ids = ','.join(map(str, int_ids))
            # get the articles from the feedbin api
            entries = get_entries({'ids':ids})

            # check if we have successfully get the requested data
            if entries['status_code'] == 200 and tags['status_code']==200:
                articles = get_articles(entries, tags) # extract the needed info from the return
                print(f'got {len(articles)} articles')

                # mark articles as read
                update_read_status(int_ids)
                
                for article in articles:
                    try:
                        # Handle single quotes on tags
                        article['tags'] = [
                            x.replace("'", "") for x in article['tags']
                        ]


                        query = f""" INSERT INTO articles (
                                        article_id, 
                                        headline, 
                                        source,
                                        summary, 
                                        tags, 
                                        timestamp, 
                                        url
                                    ) VALUES (
                                        {article['article_id']},
                                        '{article['headline'].replace("'", "''")}',
                                        '{article['source']}',
                                        '{article['summary'].replace("'", "''")}',
                                        ARRAY{article['tags']},
                                        '{str(datetime.fromtimestamp(article['timestamp']))}',
                                        '{article['url']}'
                                    ) ON CONFLICT DO NOTHING
                                """                        
                        db.engine.execute(query)
                        db.session.commit()

                        for tag in article['tags']:
                            socketio.emit('update_articles', json.dumps(article), to='articles_' + str(tag))
                    except Exception as e:
                        print(f"Error saving article: {e}")

                print('update articles status done!')
                print('ids : ', int_ids)


def delete_old_articles(app, db):
    """ Function to delete articles older than 2 days
        from Postgres database
    """
    with app.app_context():
        try:
            now = int(datetime.now().replace(microsecond=0).timestamp())
            today = datetime.fromtimestamp(now)
            expiration = today - timedelta(days=2)

            Article.query.filter(Article.timestamp <= expiration).delete()
            db.session.commit()

            print("Articles deleted successfully!")
        except Exception as e:
            print(f"Error deleting article: {e}")
