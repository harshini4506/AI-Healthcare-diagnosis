import re
from typing import List, Dict
import random
from datetime import datetime

class MentalHealthChatbot:
    def __init__(self):
        self.conversation_history = []
        self.current_topic = None
        
        # Define response templates for mental health support
        self.templates = {
            'greeting': [
                "Hi! I'm your mental health support assistant. How are you feeling today?",
                "Hello! I'm here to listen and support you. Would you like to share how you're feeling?",
                "Welcome! This is a safe space to talk about your feelings. How can I help you today?"
            ],
            'emotions': {
                'breakup': {
                    'responses': [
                        "I'm so sorry to hear about your breakup. It's completely normal to feel hurt and emotional right now.",
                        "Breakups can be really painful. I'm here to listen and support you through this.",
                        "Going through a breakup is one of the hardest experiences. Let's work through these feelings together."
                    ],
                    'techniques': [
                        "Let's try to focus on self-care right now. Could you do something nice for yourself today?",
                        "Writing down your feelings in a journal can help process emotions. Would you like to try that?",
                        "Sometimes doing a favorite activity can help take your mind off things. What activities usually bring you joy?"
                    ],
                    'suggestions': [
                        "Would you like to talk about how you're coping?",
                        "Have you been able to reach out to friends or family for support?",
                        "Sometimes a change of environment can help. Could you go for a walk or visit a favorite place?"
                    ]
                },
                'relationship_conflict': {
                    'responses': [
                        "It sounds like you're going through a difficult time in your relationship. Let's talk about it.",
                        "Relationship conflicts can be very stressful. I'm here to help you process these feelings.",
                        "It's natural to feel upset when someone close to us hurts us. Let's work through this together."
                    ],
                    'techniques': [
                        "Let's try to identify your feelings. Are you feeling hurt, angry, disappointed, or something else?",
                        "Taking some deep breaths can help us think more clearly. Would you like to try a breathing exercise?",
                        "Sometimes writing a letter (even if you don't send it) can help express your feelings."
                    ],
                    'suggestions': [
                        "Would you like to talk about what happened?",
                        "Have you tried communicating your feelings to them?",
                        "What would help you feel better right now?"
                    ]
                },
                'anxiety': {
                    'responses': [
                        "I hear that you're feeling anxious. Let's work through this together.",
                        "Anxiety can be overwhelming. Would you like to try some calming techniques?",
                        "I understand anxiety is difficult. Let's break down what's troubling you."
                    ],
                    'techniques': [
                        "Let's try a simple breathing exercise: Breathe in for 4 counts, hold for 4, out for 4.",
                        "Try grounding yourself: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
                        "Let's practice progressive muscle relaxation, starting from your toes up to your head."
                    ],
                    'suggestions': [
                        "Would you like to explore what triggered this anxiety?",
                        "Have you tried mindfulness meditation before?",
                        "Sometimes writing down our worries can help. Would you like to try that?"
                    ]
                },
                'depression': {
                    'responses': [
                        "I'm here with you, and I hear that you're feeling down.",
                        "Depression can make everything feel heavy. Let's take small steps together.",
                        "Thank you for sharing these feelings with me. You're not alone in this."
                    ],
                    'techniques': [
                        "Let's start with one small achievable goal today. What's one tiny thing you could do?",
                        "Sometimes getting out of bed is a victory. Can you celebrate that achievement?",
                        "Would you like to try some gentle self-care activities?"
                    ],
                    'suggestions': [
                        "Have you been able to get outside today?",
                        "Would you like to talk about what's been on your mind?",
                        "Sometimes connecting with others can help. Is there someone you could reach out to?"
                    ]
                },
                'stress': {
                    'responses': [
                        "It sounds like you're under a lot of stress. Let's work on managing it together.",
                        "Stress can be overwhelming. Let's break it down into smaller pieces.",
                        "I hear how stressed you are. Let's find some ways to help you cope."
                    ],
                    'techniques': [
                        "Let's try making a list of what's causing stress and tackle one thing at a time.",
                        "Taking short breaks can help. Try the 5-minute rule: just take a 5-minute breather.",
                        "Would you like to try a quick stress-relief exercise?"
                    ],
                    'suggestions': [
                        "Have you been able to take breaks between tasks?",
                        "Would you like to explore some stress management techniques?",
                        "Sometimes organizing our thoughts helps. Want to try that?"
                    ]
                },
                'overwhelmed': {
                    'responses': [
                        "It's okay to feel overwhelmed. Let's take this one step at a time.",
                        "When everything feels too much, we can start with just one small thing.",
                        "I understand you're feeling overwhelmed. Let's find a way to make things more manageable."
                    ],
                    'techniques': [
                        "Let's try breaking down what's overwhelming you into smaller, manageable parts.",
                        "Sometimes making a simple to-do list can help us feel more in control.",
                        "Would you like to try a calming visualization exercise?"
                    ],
                    'suggestions': [
                        "Can we identify what's contributing most to feeling overwhelmed?",
                        "Would you like to focus on just one thing right now?",
                        "Sometimes taking a step back helps. Would you like to try that?"
                    ]
                }
            },
            'emergency': [
                "I hear you're in crisis. Please know that help is available 24/7:",
                "If you're having thoughts of self-harm, please reach out for immediate help:",
                "Your life matters. Professional help is available right now:"
            ],
            'emergency_resources': [
                "National Crisis Hotline: 988 (US)",
                "Crisis Text Line: Text HOME to 741741",
                "Please call emergency services (911) if you're in immediate danger"
            ],
            'support': [
                "I'm here to listen without judgment. Would you like to tell me more?",
                "You're showing strength by sharing this. How can I best support you right now?",
                "Thank you for trusting me with your feelings. What would help most in this moment?"
            ],
            'healing_advice': [
                "Remember that healing takes time, and it's okay to not be okay.",
                "Focus on taking care of yourself right now - your well-being comes first.",
                "Every day might feel different, and that's completely normal."
            ]
        }
        
        # Keywords for detecting emotional states
        self.emotion_keywords = {
            'breakup': ['breakup', 'broke up', 'break up', 'ended relationship', 'ex', 'dumped', 'left me'],
            'relationship_conflict': ['fight', 'argument', 'conflict', 'scolded', 'yelled', 'angry with', 'upset with'],
            'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'fear', 'stressed out', 'uneasy'],
            'depression': ['depressed', 'sad', 'hopeless', 'empty', 'worthless', 'tired', 'lonely'],
            'stress': ['stressed', 'pressure', 'overwhelmed', 'tense', 'burnout', 'exhausted'],
            'overwhelmed': ['overwhelmed', 'too much', 'cant handle', 'cant cope', 'drowning']
        }
        
        # Emergency keywords that require immediate attention
        self.emergency_keywords = [
            'suicide', 'kill myself', 'want to die', 'end it all', 'self harm',
            'hurt myself', 'no reason to live', 'better off dead'
        ]

    def get_response(self, message: str) -> str:
        # Add message to conversation history
        self.conversation_history.append(message)
        message_lower = message.lower()

        # Check for emergency keywords first
        if any(keyword in message_lower for keyword in self.emergency_keywords):
            self.current_topic = 'emergency'
            response = random.choice(self.templates['emergency'])
            resources = "\n\n".join(self.templates['emergency_resources'])
            return f"{response}\n\n{resources}\n\nWould you like to talk about what's bringing up these thoughts?"

        # Check for greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey']):
            self.current_topic = 'greeting'
            return random.choice(self.templates['greeting'])

        # Detect emotional state
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                self.current_topic = emotion
                responses = self.templates['emotions'][emotion]
                
                # Construct a supportive response
                main_response = random.choice(responses['responses'])
                technique = random.choice(responses['techniques'])
                suggestion = random.choice(responses['suggestions'])
                support = random.choice(self.templates['support'])
                healing = random.choice(self.templates['healing_advice'])
                
                return f"{main_response}\n\n{technique}\n\n{suggestion}\n\n{support}\n\n{healing}"

        # Default response for unclear messages
        self.current_topic = 'general'
        return (
            "I understand you're going through something difficult. To help you better, could you:\n"
            "1. Tell me more about what's troubling you\n"
            "2. Share how this situation is making you feel\n"
            "3. Let me know if you'd like some coping techniques or just someone to listen"
        )

    def get_suggestions(self) -> List[str]:
        # Get suggestions based on current topic
        if not self.current_topic or self.current_topic == 'greeting':
            return [
                "I just went through a breakup",
                "I'm having relationship problems",
                "I'm feeling really hurt",
                "I need someone to talk to"
            ]
        
        if self.current_topic == 'breakup':
            return [
                "I miss them so much",
                "How do I move on?",
                "I feel so lonely",
                "Will this pain ever go away?"
            ]
        
        if self.current_topic == 'relationship_conflict':
            return [
                "They hurt my feelings",
                "How do I fix this?",
                "Should I talk to them?",
                "I need advice about my relationship"
            ]
        
        if self.current_topic == 'anxiety':
            return [
                "I need help calming down",
                "Can we try a breathing exercise?",
                "How can I stop worrying?",
                "Everything makes me nervous"
            ]
        
        if self.current_topic == 'depression':
            return [
                "I don't enjoy anything anymore",
                "How can I feel better?",
                "Everything feels hopeless",
                "I feel so alone"
            ]
        
        if self.current_topic == 'stress':
            return [
                "I can't handle the pressure",
                "Everything is too much",
                "How can I manage stress better?",
                "I need help relaxing"
            ]
        
        if self.current_topic == 'overwhelmed':
            return [
                "Can we break this down?",
                "I don't know where to start",
                "How can I cope with everything?",
                "I need help organizing my thoughts"
            ]
        
        if self.current_topic == 'emergency':
            return [
                "I need immediate help",
                "Can you tell me more about crisis resources?",
                "How can I stay safe right now?",
                "I want to talk to a professional"
            ]
        
        return [
            "Can you help me understand my feelings?",
            "What coping strategies do you suggest?",
            "I'd like to try some techniques",
            "Can we talk about something specific?"
        ] 