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
import MovieCard from '../../components/MovieCard'; // Import MovieCard component

// Re-use API URL configuration (ensure it's correct!)
const API_BASE_URL = 'http://172.16.7.45:8000/api'; // Example: 'http://192.168.1.105:8000/api'

// Define message structure
interface Message {
  id: string;
  role: 'user' | 'assistant';
  text?: string; // For text messages
  movies?: Movie[]; // For assistant responses with movies
  isTyping?: boolean; // Optional typing indicator
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
        text: data.results?.length > 0 ? undefined : "Sorry, I couldn't find any matches for that.",
        isTyping: true,
      };
      addMessage(assistantMessage);

    } catch (err: any) {
      console.error('Chat search failed:', err);
      setError(err.message || 'Failed to fetch chat results.');
      // Optionally add an error message to the chat
      addMessage({ 
          id: Date.now().toString() + '-error', 
          role: 'assistant', 
          text: `Error: ${err.message || 'Failed to fetch chat results.'}`,
          isTyping: false,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMoviePress = (movie: Movie) => {
    // Handle movie press logic
    console.log('Movie pressed:', movie);
  };

  // Render individual messages
  const renderMessage = ({ item }: { item: Message }) => {
    // If the message is from the assistant and has movies
    if (item.role === 'assistant' && item.movies && item.movies.length > 0) {
      return (
        <View style={styles.recommendationContainer}>
          {/* Header bubble for recommendations */}
          <View style={[styles.messageBubble, styles.assistantMessage, styles.headerBubble]}>
            <Text style={styles.messageText}>Here are some recommendations:</Text>
          </View>
          
          {/* Movies recommendations below the header */}
          <View style={styles.movieListOuterContainer}>
            <FlatList
              data={item.movies}
              keyExtractor={(movie) => movie.id.toString()}
              renderItem={({ item: movie }) => (
                <MovieCard 
                  title={movie.title} 
                  imageUrl={movie.poster_path ? 
                    `https://image.tmdb.org/t/p/w500${movie.poster_path}` : 
                    'https://via.placeholder.com/150x225?text=No+Image'
                  } 
                  rating={movie.vote_average || 0} 
                  year={movie.release_date ? movie.release_date.substring(0, 4) : 'N/A'} 
                  onPress={() => handleMoviePress(movie)}
                />
              )}
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.movieListContainer}
            />
          </View>
        </View>
      );
    } 
    
    // Regular messages (user or assistant without movies)
    return (
      <View
        style={[
          styles.messageBubble,
          item.role === 'user' ? styles.userMessage : styles.assistantMessage,
        ]}
      >
        <Text style={styles.messageText}>{item.content}</Text>
        {item.role === 'assistant' && item.isTyping && (
          <Text style={styles.assistantInfoText}>Typing...</Text>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "padding"} 
        style={styles.keyboardAvoiding} // Ensure KAV takes full space
      >
        {/* Title moved outside the main content/input area if needed, or keep inside container */}
        {/* Option 1: Title inside scrollable area's container */}
         <View style={styles.innerContainer}> 
            <Text style={styles.title}>Movie Chat</Text>
            
            <FlatList
              ref={flatListRef}
              data={messages}
              renderItem={renderMessage}
              keyExtractor={(item) => item.id}
              style={styles.chatArea} // List takes available space
              contentContainerStyle={styles.chatContent}
            />

            {/* Loader and Error can be tricky with KAV, maybe position absolutely or keep here? */}
             {isLoading && <ActivityIndicator size="small" color="#0000ff" style={styles.loader} />}
             {error && !isLoading && <Text style={styles.errorText}>{error}</Text>}
         </View>
          
        {/* Input container is now a direct child of KAV, pushed up by padding */}
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
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// --- Styles --- 
const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f8f8',
  },
  keyboardAvoiding: {
    flex: 1,
    // Removed container style from here, apply flex direction if needed
    // flexDirection: 'column', // KAV default might be column
  },
  // New container for the content above the input
  innerContainer: {
      flex: 1, // Takes up space above the input container
      paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 0) + 10 : 15,
      // Removed paddingBottom from here
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    paddingHorizontal: 15,
    marginBottom: 10,
    textAlign: 'center',
  },
  chatArea: {
    flex: 1, // List still takes available space within innerContainer
    paddingHorizontal: 15,
  },
  chatContent: {
     paddingBottom: 10, // Keep small padding for the last item from list edge
  },
  loader: {
    // Position loader appropriately if needed, maybe absolute?
    // position: 'absolute', top: 50, alignSelf: 'center'
    paddingVertical: 5, // Simple vertical padding for now
  },
  errorText: {
      color: 'red',
      textAlign: 'center',
      paddingHorizontal: 15,
      paddingVertical: 5, // Simple vertical padding for now
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#ccc',
    backgroundColor: '#fff',
    alignItems: 'center',
    // This container is no longer flexed, it sits at the bottom
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
    marginBottom: 20, // Increased margin further
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
    // Ensure the bubble expands with content
    alignItems: 'flex-start', // Align internal items to the start
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
  },
  recommendationContainer: {
    width: '100%', // Use full width for the container
    marginBottom: 20,
    paddingTop: 10, // Add padding at top to prevent overlap
  },
  headerBubble: {
    marginBottom: 10, // Space between header and movies
  },
  movieListOuterContainer: {
    paddingLeft: 5, // Slight indent for the movie list
    width: '95%', // Slightly less than full width
  },
}); 