from typing import Callable, Optional


from slackapp2pyez.request.all import AnyRequest
from slackapp2pyez.web.classes.view import View
from slackapp2pyez.exceptions import SlackAppError
from slackapp2pyez import SlackApp

__all__ = [
    'Modal',
    'View'
]


def with_callback(meth):
    def wrapper(self, *args, callback: Callable = None, **kwargs):
        cbk = callback or self.callback
        if cbk:
            self.app.ic.view.on(self.view.callback_id, cbk)

        if self.notify_on_close:
            self.view.notify_on_close = True
            self.app.ic.view_closed.on(
                self.view.callback_id,
                self.notify_on_close
            )

        return meth(self, *args, **kwargs)

    return wrapper


class Modal(object):
    def __init__(
        self,
        rqst: AnyRequest,
        view: Optional[View] = None,
        detached: Optional[bool] = False,
        callback: Optional[Callable] = None
    ):
        """

        Parameters
        ----------
        rqst : Request
            The originating request that this Modal will be bound to.
            If this request contains a view attribute it means that the
            request was a result of a view_* interactive response, for
            example view_submission.  This rqst.view will then become
            the basis for the Modal.view

        view : View
            If provided will be the basis of the Modal view instance.

        detached : bool
            If this Modal is being used outside the context of the Slack
            general process, for example running in a backthrough Thread,
            then set this to True so that the methods operating on the
            modal, for example update(), execute as required.
        """
        self.rqst = rqst
        self.app: SlackApp = rqst.app

        def from_payload_or_new():
            if 'view' in rqst.rqst_data:
                return View.from_view(rqst.rqst_data['view'])

            return View()

        self.view = view or from_payload_or_new()
        self.detached = detached
        self.callback = callback
        self.notify_on_close = None

    @with_callback
    def open(self):
        return self.rqst.client.views_open(
            trigger_id=self.rqst.trigger_id,
            view=self.view.to_dict())

    @with_callback
    def update(self):
        if self.rqst.rqst_type == 'view_submission' and not self.detached:
            return self.view.update_response()

        if hasattr(self.view, 'view_id'):
            kwargs = dict(
                view=self.view.to_dict(),
                view_id=self.view.view_id
            )

            if not self.detached:
                kwargs['hash'] = self.view.view_hash

            return self.rqst.client.views_update(**kwargs)

        raise SlackAppError(
            f'Attempting to update view in unknown context'
        )

    @with_callback
    def push(self):
        if self.rqst.rqst_type == 'view_submission':
            return self.view.push_response()

        return self.rqst.client.views_push(
            trigger_id=self.rqst.trigger_id,
            view=self.view.to_dict()
        )
