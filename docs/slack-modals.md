## Regarding View Close Button vs. [X]

If a user closes a specific view in a modal using the _Cancel_ button, you will
receive a `view_closed` event with the corresponding view's id. 

However, if the user exits the modal with the `[x]` in the top-right corner,
you'll receive a `view_closed` event with the initial modal view's id and the
`is_cleared` flag set to true.
