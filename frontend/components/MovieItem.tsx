import React from 'react';
import { View, Text, Image, StyleSheet, Dimensions } from 'react-native';

// Define the structure of a movie item based on SearchResultItem from the backend
export interface Movie {
  id: string;
  title?: string;
  release_date?: string;
  genres?: string;
  overview?: string;
  poster_path?: string;
  distance: number;
}

// Base URL for TMDB poster images (adjust size as needed, e.g., w342, w500, w780)
const TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w185';

interface MovieItemProps {
  movie: Movie;
}

const MovieItem: React.FC<MovieItemProps> = ({ movie }) => {
  const posterUrl = movie.poster_path 
    ? `${TMDB_IMAGE_BASE_URL}${movie.poster_path}` 
    : undefined; // Handle cases where poster path might be null

  return (
    <View style={styles.container}>
      {posterUrl ? (
        <Image source={{ uri: posterUrl }} style={styles.poster} resizeMode="cover" />
      ) : (
        <View style={[styles.poster, styles.placeholderPoster]} /> // Placeholder if no image
      )}
      <View style={styles.infoContainer}>
        <Text style={styles.title}>{movie.title ?? 'No Title'}</Text>
        <Text style={styles.details}>Release: {movie.release_date ?? 'N/A'}</Text>
        <Text style={styles.details}>Genres: {movie.genres ?? 'N/A'}</Text>
        {/* <Text style={styles.details}>Distance: {movie.distance.toFixed(4)}</Text> */}
        <Text style={styles.overview} numberOfLines={3} ellipsizeMode="tail">
          {movie.overview ?? 'No Overview'}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    padding: 10,
    marginBottom: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    elevation: 2,
    alignItems: 'center', // Align items vertically
  },
  poster: {
    width: 80, 
    height: 120, // Maintain aspect ratio typical for posters
    borderRadius: 4,
    marginRight: 10,
  },
  placeholderPoster: {
    backgroundColor: '#e0e0e0', // Placeholder color
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoContainer: {
    flex: 1, // Take remaining space
    justifyContent: 'center',
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  details: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  overview: {
    fontSize: 12,
    color: '#333',
    marginTop: 4,
  },
});

export default MovieItem; 