import React, { useState } from 'react';
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
} from 'react-native';
import MovieItem, { Movie } from '../../components/MovieItem'; // Import the component and type

// --- Configuration ---
// IMPORTANT: Replace <YOUR_MACHINE_LOCAL_IP> with your actual backend server's local IP address.
// If running backend locally and testing on a simulator/emulator: use your machine's local IP.
// If testing on a physical device, ensure it's on the same network and use the machine's local IP.
// Do NOT use 'localhost' unless the backend is also running on the device itself.
const API_BASE_URL = 'http://172.16.7.45:8000/api'; // Example: 'http://192.168.1.105:8000/api'

export default function SearchScreen() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query.');
      return;
    }

    console.log(`Searching for: ${query}`);
    setIsLoading(true);
    setError(null);
    setResults([]); // Clear previous results
    Keyboard.dismiss(); // Hide keyboard

    try {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_text: query,
          n_results: 10, // Request 10 results
        }),
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
            const errorJson = await response.json();
            errorDetail = errorJson.detail || errorDetail;
        } catch (e) {
            // Ignore if response is not JSON
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      // console.log('Search results:', data.results);
      setResults(data.results || []); // Ensure results is always an array

    } catch (err: any) {
      console.error('Search failed:', err);
      setError(err.message || 'Failed to fetch search results. Check backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.title}>Movie Search</Text>
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.input}
            placeholder="Enter movie description..."
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={handleSearch} // Allow searching by pressing return/enter
          />
          <Button title="Search" onPress={handleSearch} disabled={isLoading} />
        </View>

        {isLoading && <ActivityIndicator size="large" color="#0000ff" style={styles.loader} />}

        {error && <Text style={styles.errorText}>{error}</Text>}

        {!isLoading && !error && results.length === 0 && !query && (
             <Text style={styles.infoText}>Enter a query to search for movies.</Text>
        )}

         {!isLoading && !error && results.length === 0 && query && (
             <Text style={styles.infoText}>No results found for \"{query}\".</Text>
         )}


        <FlatList
          data={results}
          renderItem={({ item }) => <MovieItem movie={item} />}
          keyExtractor={(item) => item.id}
          style={styles.list}
          contentContainerStyle={styles.listContent}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f0f0f0', // Background for the whole screen area
  },
  container: {
    flex: 1,
    paddingHorizontal: 15, // Keep horizontal padding
    paddingBottom: 15, // Keep bottom padding
    // Add platform-specific top padding, providing a fallback for currentHeight
    paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight ?? 0) + 10 : 15, 
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    marginBottom: 15,
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    paddingHorizontal: 10,
    paddingVertical: 8,
    marginRight: 10,
    borderRadius: 5,
    backgroundColor: '#fff',
  },
  loader: {
    marginTop: 20,
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginTop: 10,
    marginBottom: 10,
  },
  infoText: {
      textAlign: 'center',
      marginTop: 20,
      fontSize: 16,
      color: '#555',
  },
  list: {
    flex: 1, // Ensure list takes available space
  },
  listContent: {
     paddingBottom: 20, // Add padding at the bottom of the scrollable content
  }
});
