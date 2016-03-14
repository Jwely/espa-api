
class MockError(object):

    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
        self.extra = {'retry_after': 9, 'retry_limit': 10}
def resolve_submitted(error_message, name):
    return MockError('submitted', 'a reason')

def resolve_unavailable(error_message, name):
    return MockError('unavailable', 'a reason')

def resolve_retry(error_message, name):
    return MockError('retry', 'a reason')



