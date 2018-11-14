# from user_agents import parse


# ua_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
# user_agent = parse(ua_string)
# print(dir(user_agent))


# pr = f"""
# is_bot = {user_agent.is_bot}
# is_email_client = {user_agent.is_email_client}
# is_mobile = {user_agent.is_mobile}
# is_pc = {user_agent.is_pc}
# is_tablet = {user_agent.is_tablet}
# is_touch_capable = {user_agent.is_touch_capable}
# device.family = {user_agent.device.family }
# device.model = {user_agent.device.model   }
# os.family = {user_agent.os.family    }
# os.version = {user_agent.os.version_string   }
# browseros.family = {user_agent.browser.family    }
# browser.version = {user_agent.browser.version_string   }

# """
# print(pr)


def a(f): return f & 2 == 2


print(a(3))
