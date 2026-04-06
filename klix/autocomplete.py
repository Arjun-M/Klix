from prompt_toolkit.completion import Completer, Completion, FuzzyWordCompleter

class KlixCompleter(Completer):
    def __init__(self, commands_dict, custom_completers, session):
        self.commands = commands_dict
        self.custom_completers = custom_completers
        self.session = session
        
        self.command_words = []
        for cmd in self.commands.values():
            self.command_words.append(cmd.name)
            self.command_words.extend(cmd.aliases)
            
        self.command_words = list(set(self.command_words))
        self.fuzzy_cmd_completer = FuzzyWordCompleter(self.command_words)
        
    def get_completions(self, document, complete_event):
        text = document.text
        if " " not in text:
            # Complete command names and aliases fuzzy match
            yield from self.fuzzy_cmd_completer.get_completions(document, complete_event)
        else:
            # Complete arguments
            parts = text.split(" ", 1)
            cmd_name = parts[0]
            real_cmd = self.commands.get(cmd_name)
            if real_cmd and real_cmd.name in self.custom_completers:
                arg_text = parts[1]
                suggestions = self.custom_completers[real_cmd.name](arg_text, self.session)
                # Apply simple fuzzy matching for custom suggestions too
                for suggestion in suggestions:
                    if arg_text.lower() in suggestion.lower():
                        yield Completion(suggestion, start_position=-len(arg_text))
