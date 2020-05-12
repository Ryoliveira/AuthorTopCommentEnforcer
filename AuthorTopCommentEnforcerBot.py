import praw
import os
import time


class AuthorTopCommentBot:
    DEADLINE_MINUTES = 15
    FLAIR_LIST = ["TEST"]
    SUBREDDIT = "RyoliveiraTest"

    def __init__(self):
        self.reddit = None
        self.submissions = []
        self.current_submission = None
        self.author_meets_requirement = None
        self.ids_to_ignore = []

    def log_in(self):
        self.reddit = praw.Reddit(client_id=os.environ.get('CLIENT_ID'),
                                  client_secret=os.environ.get('CLIENT_SECRET'),
                                  user_agent="AuthorTopCommentBot v1.0",
                                  username=os.environ.get('USERNAME'),
                                  password=os.environ.get('PASSWORD'))

    def get_submissions(self):
        new_submissions = self.reddit.subreddit(self.SUBREDDIT).new(limit=50)
        for sub in new_submissions:
            if sub.link_flair_text in self.FLAIR_LIST:
                minutes_since_creation = (time.time() - sub.created_utc) // 60
                if minutes_since_creation >= self.DEADLINE_MINUTES and sub.id not in self.ids_to_ignore:
                    self.submissions.append(sub)
        # cant populate the list
        # self.submissions = [sub for sub in new_submissions if ((time.time() - sub.created_utc) // 60) >= 15]

    def check_submission_for_author_comment(self):
        self.author_meets_requirement = False
        for comment in self.current_submission.comments:
            if comment.author == self.current_submission.author:
                if len(comment.body.replace("\\s", "")) >= 40:
                    self.author_meets_requirement = True

    def process_decision(self):
        if self.author_meets_requirement:
            print("Submission meets requirement")
            self.write_id_to_file()
        else:
            print(f"Deleting submission - Title: {self.current_submission.title}, "
                  f"Author: {self.current_submission.author}")
            self.current_submission.mod.remove()
            self.current_submission.mod.send_removal_message(message="With every post you must proved a comment ",
                                                             title="Comment requirement not met",
                                                             type="private")

    def get_ignore_ids(self):
        with open("submission_ids.txt", "r") as id_file:
            self.ids_to_ignore = [submission_id for submission_id in id_file.readlines()]

    def write_id_to_file(self):
        with open("submission_ids.txt", "a") as id_file:
            id_file.write(self.current_submission.id)

    def run_bot(self):
        self.log_in()
        self.get_ignore_ids()
        while True:
            self.get_submissions()
            for submission in self.submissions:
                print(submission)
                self.current_submission = submission
                self.check_submission_for_author_comment()
                self.process_decision()
                self.ids_to_ignore.append(submission.id)
            self.submissions.clear()


if __name__ == '__main__':
    bot = AuthorTopCommentBot()
    bot.run_bot()
