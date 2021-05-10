import requests
import traceback

from datetime import datetime

import pandas as pd

subreddit = "wallstreetbets"

url = "https://api.pushshift.io/reddit/{}/search?limit=1000&sort=desc&subreddit={}&before="

submission_df = pd.DataFrame(None, columns=[
    "id", "title", "score",
    "author", "author_flair_text", "removed_by", "total_awards_received",
    "awarders",
    "created_utc", "full_link", "num_comments",
    "over_18",
])

start_time = datetime.utcnow()


def downloadFromUrl(df, object_type):
    count = 0
    previous_epoch = int(start_time.timestamp())
    values = []
    if len(values) > 0:
        previous_epoch = values[-1]['created_utc'] - 1
    print(f"Saving {object_type}s")

    while True:
        new_url = url.format(object_type, subreddit) + str(previous_epoch)
        json = requests.get(new_url)
        try:
            json_data = json.json()
        except:
            print(json)
        else:
            if 'data' not in json_data:
                break
            objects = json_data['data']
            if len(objects) == 0:
                break

            for submission in objects:
                previous_epoch = submission['created_utc'] - 1
                count += 1
                if object_type == 'comment':
                    try:
                        handle.write(str(submission['score']))
                        handle.write(" : ")
                        handle.write(datetime.fromtimestamp(submission['created_utc']).strftime("%Y-%m-%d"))
                        handle.write("\n")
                        text = submission['body']
                        textASCII = text.encode(encoding='ascii', errors='ignore').decode()
                        handle.write(textASCII)
                        handle.write("\n-------------------------------\n")
                    except Exception as err:
                        print(f"Couldn't print comment: https://www.reddit.com{submission['permalink']}")
                        print(traceback.format_exc())

                elif object_type == 'submission':
                    if 'awarders' in submission:
                        awarders = submission['awarders']
                    else:
                        awarders = None
                    if 'total_awards_received' in submission:
                        total_awards = submission['total_awards_received']
                    else:
                        total_awards = None
                    if 'removed_by_category' in submission:
                        removed_by = submission['removed_by_category']
                    else:
                        removed_by = None

                    try:
                        values.append(dict(zip(submission_df.columns,
                                               [submission['id'], submission['title'], submission['score'],
                                                submission['author'],
                                                submission['author_flair_text'], removed_by,
                                                total_awards, awarders, submission['created_utc'],
                                                submission['full_link'], submission['num_comments'],
                                                submission['over_18']])))
                    except Exception as err:
                        print(f"Couldn't print post: {submission['url']}")
                        print(traceback.format_exc())

        print(
            f"Saved {len(values)} of {count} {object_type}s through {datetime.fromtimestamp(previous_epoch).strftime('%Y-%m-%d')}")

    print(f"Saved {count} {object_type}s")
    return values


new_values = downloadFromUrl(submission_df, "submission")
submission_df = submission_df.append(new_values, ignore_index=False)
submission_df.to_csv(f'r_{subreddit}_posts.csv', index=False)
