from game_abc import AbstractGame, GameMove, GameHistory
from typing import Dict, Any, Optional, List, Tuple
import random
import time

# Define card values
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

SUITES = ['♠', '♥', '♦', '♣']

# Define possible player actions
ACTIONS = ['hit', 'stand', 'double', 'split']

class Card:
    def __init__(self, rank: str, suite: str):
        self.rank = rank
        self.suite = suite
        self.face_up = False

    def __str__(self):
        return f"{self.rank}{self.suite}"

    def __repr__(self):
        return str(self)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rank': self.rank,
            'suite': self.suite,
            'face_up': self.face_up
        }

class Hand:
    def __init__(self, cards: Optional[List[Card]] = None):
        self.cards = cards or []
        self.bet = 0
        self.is_split = False
        self.is_double = False
        self.is_surrendered = False

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def get_value(self) -> int:
        """Calculate the value of the hand"""
        value = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
            else:
                value += CARD_VALUES[card.rank]
        
        # Handle aces
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        
        return value

    def is_bust(self) -> bool:
        return self.get_value() > 21

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.get_value() == 21

    def can_split(self) -> bool:
        return (len(self.cards) == 2 and 
                self.cards[0].rank == self.cards[1].rank and 
                not self.is_split)

    def can_double(self) -> bool:
        return len(self.cards) == 2 and not self.is_double

    def to_dict(self) -> Dict[str, Any]:
        return {
            'cards': [card.to_dict() for card in self.cards],
            'value': self.get_value(),
            'is_bust': self.is_bust(),
            'is_blackjack': self.is_blackjack(),
            'bet': self.bet,
            'is_split': self.is_split,
            'is_double': self.is_double,
            'is_surrendered': self.is_surrendered
        }

class BlackjackGame(AbstractGame):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.deck = []
        self.player_hands = []
        self.dealer_hand = Hand()
        self.current_hand_idx = 0
        self.shoe_size = 6  # Number of decks in shoe
        self.min_bet = 10
        self.max_bet = 1000
        self._init_game()

    def _init_game(self):
        """Initialize a new game"""
        self._create_shoe()
        self.player_hands = []
        self.dealer_hand = Hand()
        self.current_hand_idx = 0

    def _create_shoe(self):
        """Create a new shoe with multiple decks"""
        self.deck = []
        for _ in range(self.shoe_size):
            for rank in CARD_VALUES:
                for suite in SUITES:
                    self.deck.append(Card(rank, suite))
        random.shuffle(self.deck)

    def _deal_card(self, face_up: bool = True) -> Card:
        """Deal a card from the deck"""
        if not self.deck:
            self._create_shoe()
        card = self.deck.pop()
        card.face_up = face_up
        return card

    def _init_deal(self, bets: List[int]) -> None:
        """Deal initial cards to player and dealer"""
        # Create player hands
        self.player_hands = [Hand() for _ in bets]
        for hand, bet in zip(self.player_hands, bets):
            hand.bet = bet
            
        # Deal first card to each player
        for hand in self.player_hands:
            hand.add_card(self._deal_card(True))
        
        # Deal first card to dealer (face down)
        self.dealer_hand.add_card(self._deal_card(False))
        
        # Deal second card to each player
        for hand in self.player_hands:
            hand.add_card(self._deal_card(True))
        
        # Deal second card to dealer (face up)
        self.dealer_hand.add_card(self._deal_card(True))

    def _resolve_hand(self, hand: Hand) -> Dict[str, Any]:
        """Resolve a single hand and determine outcome"""
        dealer_value = self.dealer_hand.get_value()
        player_value = hand.get_value()
        
        if hand.is_surrendered:
            return {'outcome': 'surrender', 'payout': -hand.bet/2}
            
        if hand.is_bust():
            return {'outcome': 'lose', 'payout': -hand.bet}
            
        if self.dealer_hand.is_bust():
            return {'outcome': 'win', 'payout': hand.bet * 2}
            
        if hand.is_blackjack() and not self.dealer_hand.is_blackjack():
            return {'outcome': 'blackjack', 'payout': hand.bet * 2.5}
            
        if self.dealer_hand.is_blackjack() and not hand.is_blackjack():
            return {'outcome': 'lose', 'payout': -hand.bet}
            
        if player_value > dealer_value:
            return {'outcome': 'win', 'payout': hand.bet * 2}
        elif player_value < dealer_value:
            return {'outcome': 'lose', 'payout': -hand.bet}
        else:
            return {'outcome': 'push', 'payout': hand.bet}

    def _dealer_play(self) -> None:
        """Play dealer's hand according to standard rules"""
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self._deal_card(True))

    def validate_action(self, action: str, hand_idx: int) -> bool:
        """Validate if the action is legal for the current hand"""
        if hand_idx >= len(self.player_hands):
            return False
            
        hand = self.player_hands[hand_idx]
        
        if action == 'hit':
            return not hand.is_bust()
            
        if action == 'stand':
            return True
            
        if action == 'double':
            return hand.can_double()
            
        if action == 'split':
            return hand.can_split()
            
        return False

    def make_action(self, action: str, hand_idx: int = 0) -> Dict[str, Any]:
        """Execute a player action"""
        if not self.validate_action(action, hand_idx):
            raise ValueError(f"Invalid action: {action}")
            
        hand = self.player_hands[hand_idx]
        
        if action == 'hit':
            hand.add_card(self._deal_card(True))
            
        elif action == 'stand':
            self.current_hand_idx += 1
            if self.current_hand_idx >= len(self.player_hands):
                self._dealer_play()
                
        elif action == 'double':
            hand.is_double = True
            hand.bet *= 2
            hand.add_card(self._deal_card(True))
            self.current_hand_idx += 1
            if self.current_hand_idx >= len(self.player_hands):
                self._dealer_play()
                
        elif action == 'split':
            # Create new hand with second card
            new_hand = Hand()
            new_hand.bet = hand.bet
            new_hand.add_card(hand.cards.pop())
            self.player_hands.insert(hand_idx + 1, new_hand)
            
            # Deal new cards to both hands
            hand.add_card(self._deal_card(True))
            new_hand.add_card(self._deal_card(True))
            
            hand.is_split = True
            new_hand.is_split = True
            
            # Reset current hand index
            self.current_hand_idx = hand_idx
            
        return self.get_game_state()

    def make_bet(self, bets: List[int]) -> Dict[str, Any]:
        """Make initial bets and start the game"""
        if not all(self.min_bet <= bet <= self.max_bet for bet in bets):
            raise ValueError(f"Bets must be between {self.min_bet} and {self.max_bet}")
            
        self._init_deal(bets)
        return self.get_game_state()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        dealer_visible = self.dealer_hand.cards[1] if len(self.dealer_hand.cards) > 1 else None
        dealer_value = self.dealer_hand.get_value() if dealer_visible else 0
        
        return {
            'dealer': {
                'visible_card': dealer_visible.to_dict() if dealer_visible else None,
                'value': dealer_value,
                'hand': self.dealer_hand.to_dict()
            },
            'player_hands': [hand.to_dict() for hand in self.player_hands],
            'current_hand_idx': self.current_hand_idx,
            'legal_actions': self._get_legal_actions(),
            'game_over': self._is_game_over(),
            'outcomes': self._get_outcomes() if self._is_game_over() else None
        }

    def _get_legal_actions(self) -> List[str]:
        """Get list of legal actions for current hand"""
        if self.current_hand_idx >= len(self.player_hands):
            return []
            
        hand = self.player_hands[self.current_hand_idx]
        actions = []
        
        if not hand.is_bust():
            actions.append('hit')
        actions.append('stand')
        
        if hand.can_double():
            actions.append('double')
        
        if hand.can_split():
            actions.append('split')
            
        return actions

    def _is_game_over(self) -> bool:
        """Check if the game is over"""
        return (self.current_hand_idx >= len(self.player_hands) and 
                all(hand.is_bust() or hand.is_double or hand.is_split 
                    for hand in self.player_hands))

    def _get_outcomes(self) -> List[Dict[str, Any]]:
        """Get outcomes for all hands"""
        if not self._is_game_over():
            return None
            
        outcomes = []
        for hand in self.player_hands:
            outcome = self._resolve_hand(hand)
            outcomes.append({
                'hand': hand.to_dict(),
                'outcome': outcome['outcome'],
                'payout': outcome['payout']
            })
        return outcomes
