def try_action(action):
    def wrapper(self):
        try:
            action(self)
        except Exception as e:
            print(e)
    return wrapper