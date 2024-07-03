WelcomeText = """
Hi **%(first_name)s**, send me a file to instantly generate file links.

Join @elupdates for updates.
"""

HelpText = """
/start - Start
/help - Help
/info - User Info
/logs - Logs
/stats - User Count
/ban - Ban User
/unban - Unban User
/broadcast - Reply to a message to broadcast
"""

UserInfoText = """
**First Name:**
`{sender.first_name}`

**Last Name:**
`{sender.last_name}`

**User ID:**
`{sender.id}`

**Username:**
`@{sender.username}`
"""

FileLinksText = """
**Download Link:**
`%(dl_link)s`
**Telegram File:**
`%(tg_link)s`
"""

MediaLinksText = """
**Download Link:**
`%(dl_link)s`
**Stream Link:**
`%(stream_link)s`
**Telegram File:**
`%(tg_link)s`
"""

InvalidQueryText = """
Query data mismatched.
"""

MessageNotExist = """
File revoked or not exist.
"""

LinkRevokedText = """
The link has been revoked. It may take some time for the changes to take effect.
"""

InvalidPayloadText = """
Invalid payload.
"""

MediaTypeNotSupportedText = """
Sorry, this media type is not supported.
"""
