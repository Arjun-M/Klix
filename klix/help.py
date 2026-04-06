from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App

class HelpGenerator:
    def __init__(self, app: "App"): # Accept App instance to access its commands
        self.app = app

    def generate_help(self) -> str:
        lines = []
        processed_commands = set() # Use set of command objects to avoid alias duplicates
        
        # Sort commands by name for consistent output
        # Access commands via app._commands
        sorted_command_names = sorted(self.app._commands.keys())
        
        for name in sorted_command_names:
            cmd = self.app._commands[name]
            if cmd in processed_commands:
                continue # Already processed this command via another alias/name
            processed_commands.add(cmd)
            
            # Collect all names (including aliases) for this command
            names_for_cmd = [k for k, v in self.app._commands.items() if v == cmd]
            name_str = ", ".join(sorted(names_for_cmd)) # Sort aliases too
            
            args_str = ""
            if cmd.args_schema:
                schema = cmd.args_schema
                for field_name, field_info in schema.model_fields.items():
                    if field_info.is_required():
                        args_str += f" <{field_name}>"
                    else:
                        if field_info.annotation is bool:
                            args_str += f" [--{field_name}]"
                        else:
                            args_str += f" [--{field_name} value]"
                            
            usage = f"{name_str}{args_str}"
            lines.append(f"{usage:<35} {cmd.help}")
        return "\n".join(lines)
