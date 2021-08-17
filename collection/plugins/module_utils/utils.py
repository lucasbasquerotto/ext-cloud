def raise_for_status(response, ignore_status=None):
  if not response.ok:
    if response.status_code not in (ignore_status or []):
      errorMsg = (
          '[' + str(response.status_code) + '] ' + response.reason
          + ' (' + response.request.method + ' ' + response.url + '): '
          + response.text
      )
      raise Exception(errorMsg)
