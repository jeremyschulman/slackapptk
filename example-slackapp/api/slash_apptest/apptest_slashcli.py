from app_data import slackapp

slashcli = slackapp.add_slash_command(
    cmd='apptest',
    description='Test app components')
