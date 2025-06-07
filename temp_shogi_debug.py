import sys
import os
import inspect # For more detailed inspection

# Ensure the project root is in the Python path
# This assumes temp_shogi_debug.py is in the project root
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current sys.path: {sys.path}")

print(f"\nAttempting to import ShogiGame from games.shogi...")
try:
    from games.shogi import ShogiGame
    print("ShogiGame imported successfully.")
    
    print(f"\nInspecting ShogiGame:")
    print(f"  ShogiGame module: {ShogiGame.__module__}")
    print(f"  ShogiGame file: {inspect.getfile(ShogiGame)}")
    print(f"  ShogiGame MRO: {ShogiGame.__mro__}")
    # __abstractmethods__ is a frozenset of names of abstract methods
    # It's an attribute of the class itself.
    shogi_abstract_methods = getattr(ShogiGame, '__abstractmethods__', None)
    print(f"  ShogiGame.__abstractmethods__: {shogi_abstract_methods}")
    if shogi_abstract_methods:
        print(f"  ShogiGame is considered abstract. Unimplemented methods: {', '.join(shogi_abstract_methods)}")

    # Check for initialize_game specifically
    if 'initialize_game' in dir(ShogiGame):
        init_game_method = ShogiGame.initialize_game
        print(f"  ShogiGame.initialize_game: {init_game_method}")
        print(f"    Is it directly from ShogiGame? {init_game_method == ShogiGame.__dict__.get('initialize_game')}")
        if hasattr(init_game_method, '__isabstractmethod__'):
             print(f"ShogiGame.initialize_game __isabstractmethod__: {getattr(ShogiGame.initialize_game, '__isabstractmethod__', 'N/A')}")
    print(f"ShogiGame.initialize_game signature: {inspect.signature(ShogiGame.initialize_game)}")


    print("\nAttempting to import AbstractGame from game_abc...")
    from game_abc import AbstractGame
    print("AbstractGame imported successfully.")
    print(f"\nInspecting AbstractGame:")
    print(f"  AbstractGame module: {AbstractGame.__module__}")
    print(f"  AbstractGame file: {inspect.getfile(AbstractGame)}")
    print(f"  AbstractGame MRO: {AbstractGame.__mro__}")
    ag_abstract_methods = getattr(AbstractGame, '__abstractmethods__', None)
    print(f"  AbstractGame.__abstractmethods__: {ag_abstract_methods}")
    if ag_abstract_methods:
         print(f"  AbstractGame is abstract. Declared abstract methods: {', '.join(ag_abstract_methods)}")

    # Check for initialize_game specifically
    if 'initialize_game' in dir(AbstractGame):
        ag_init_game_method = AbstractGame.initialize_game
        print(f"  AbstractGame.initialize_game: {ag_init_game_method}")
        if hasattr(ag_init_game_method, '__isabstractmethod__'):
             print(f"AbstractGame.initialize_game __isabstractmethod__: {getattr(AbstractGame.initialize_game, '__isabstractmethod__', 'N/A')}")
    print(f"AbstractGame.initialize_game signature: {inspect.signature(AbstractGame.initialize_game)}")


    print("\nAttempting to instantiate ShogiGame('temp_test_123')...")
    game_instance = ShogiGame(game_id="temp_test_123")
    print("ShogiGame instantiated successfully!")
    # print(f"Game state: {game_instance.get_game_state()}") # This might fail if initialize_game isn't called by __init__
    print(f"Game instance type: {type(game_instance)}")

except Exception as e:
    print(f"\nERROR during import or instantiation: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
