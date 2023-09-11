from abc import ABC, abstractmethod


class DataManagerInterface(ABC):

    @abstractmethod
    def list_all_users(self):
        pass

    @abstractmethod
    def list_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_user(self, user):
        pass

    @abstractmethod
    def add_movie(self, user):
        pass

    @abstractmethod
    def update_movie(self, user):
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        pass
