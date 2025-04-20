import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  TextInput,
  Button,
  FlatList,
  Text,
  StyleSheet,
  ActivityIndicator,
  SafeAreaView,
  Keyboard,
  Platform,
  StatusBar,
  KeyboardAvoidingView,
} from 'react-native';
import MovieItem, { Movie } from '../../components/MovieItem'; // Reuse MovieItem

// Re-use API URL configuration (ensure it's correct!)
const API_BASE_URL = 'http://172.16.7.45:8000/api'; // Example: 'http://192.168.1.105:8000/api'

// Define message structure
interface Message {
  id: string;
  role: 'user' | 'assistant';
  text?: string; // For text messages
  movies?: Movie[]; // For assistant responses with movies
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const flatListRef = useRef<FlatList>(null);

  // Function to add a new message and scroll
  const addMessage = (newMessage: Message) => {
    setMessages(prev => [...prev, newMessage]);
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const handleSend = async () => {
    const userMessageText = inputText.trim();
    if (!userMessageText || isLoading) {
      return;
    }

    Keyboard.dismiss();
    setInputText('');
    setError(null);

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString() + '-user', 
      role: 'user',
      text: userMessageText,
    };
    addMessage(userMessage);
    
    setIsLoading(true);

    // Prepare conversation history for API
    const apiMessages = [...messages, userMessage].map(msg => ({
        role: msg.role,
        // Send movie data as simple text placeholder for now, 
        // or structure assistant messages differently if backend needs it
        content: msg.text ?? "[movie recommendations shown]" 
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/chat_search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: apiMessages,
          n_results: 5, // Number of results for chat
        }),
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
            const errorJson = await response.json();
            errorDetail = errorJson.detail || errorDetail;
        } catch (e) { /* Ignore */ }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      
      // Add assistant response with movies
      const assistantMessage: Message = {
        id: Date.now().toString() + '-assistant',
        role: 'assistant',
        movies: data.results || [],
        text: data.results?.length > 0 ? undefined : "Sorry, I couldn't find any matches for that."
      };
      addMessage(assistantMessage);

    } catch (err: any) {
      console.error('Chat search failed:', err);
      setError(err.message || 'Failed to fetch chat results.');
      // Optionally add an error message to the chat
      addMessage({ 
          id: Date.now().toString() + '-error', 
          role: 'assistant', 
          text: `Error: ${err.message || 'Failed to fetch chat results.'}` 
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Render individual messages
  const renderMessage = ({ item }: { item: Message }) => {
    if (item.role === 'user') {
      return (
        <View style={[styles.messageBubble, styles.userMessage]}>
          <Text style={styles.messageText}>{item.text}</Text>
        </View>
      );
    }

    // Assistant message (can contain text OR movies)
    return (
      <View style={[styles.messageBubble, styles.assistantMessage]}>
        {item.text && (
            <Text style={styles.messageText}>{item.text}</Text>
        )}
        {item.movies && item.movies.length > 0 && (
          <View style={styles.movieListContainer}>
            <Text style={styles.assistantInfoText}>Here are some recommendations:</Text>
            {item.movies.map(movie => (
              <MovieItem key={movie.id} movie={movie} />
            ))}
          </View>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardAvoiding}
        keyboardVerticalOffset={Platform.OS === "ios" ? 60 : 0} // Adjust offset as needed
      >
        <View style={styles.container}>
          <Text style={styles.title}>Movie Chat</Text>
          
          <FlatList
            ref={flatListRef}
            data={messages}
            renderItem={renderMessage}
            keyExtractor={(item) => item.id}
            style={styles.chatArea}
            contentContainerStyle={styles.chatContent}
          />

          {isLoading && <ActivityIndicator size="small" color="#0000ff" style={styles.loader} />}
          {error && !isLoading && <Text style={styles.errorText}>{error}</Text>}
          
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Ask about movies..."
              value={inputText}
              onChangeText={setInputText}
              onSubmitEditing={handleSend}
              editable={!isLoading}
            />
            <Button title="Send" onPress={handleSend} disabled={isLoading || !inputText.trim()} />
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// --- Styles --- (Combine and adapt styles)
const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f8f8',
  },
  keyboardAvoiding: {
    flex: 1,
  },
  container: {
    flex: 1,
    paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 0) + 10 : 15,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    paddingHorizontal: 15,
    marginBottom: 10,
    textAlign: 'center',
  },
  chatArea: {
    flex: 1,
    paddingHorizontal: 15,
  },
  chatContent: {
     paddingBottom: 10, 
  },
  loader: {
    marginVertical: 5,
  },
  errorText: {
      color: 'red',
      textAlign: 'center',
      paddingHorizontal: 15,
      marginVertical: 5,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#ccc',
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    paddingHorizontal: 10,
    paddingVertical: 8,
    marginRight: 10,
    borderRadius: 20, // Rounded input
    backgroundColor: '#fff',
  },
  messageBubble: {
    padding: 10,
    borderRadius: 15,
    marginBottom: 10,
    maxWidth: '80%', 
  },
  userMessage: {
    backgroundColor: '#DCF8C6', // Light green for user
    alignSelf: 'flex-end',
    borderBottomRightRadius: 0,
  },
  assistantMessage: {
    backgroundColor: '#ECECEC', // Light gray for assistant
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 0,
  },
  messageText: {
    fontSize: 16,
  },
  movieListContainer: {
      marginTop: 8,
  },
  assistantInfoText: {
      fontSize: 14,
      fontStyle: 'italic',
      color: '#555',
      marginBottom: 5,
  }
}); 