import { Tabs } from 'expo-router';
import React from 'react';

// Import Ionicons for tab bar icons
import { Ionicons } from '@expo/vector-icons'; 

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        // Styling for tabs
        tabBarActiveTintColor: '#0a7ea4', // Match the link color from not-found page
        tabBarInactiveTintColor: '#666',
        tabBarStyle: {
          borderTopWidth: 1,
          borderTopColor: '#e0e0e0',
        }
      }}>
      <Tabs.Screen
        name="index" // Search screen
        options={{
          title: 'Search',
          tabBarIcon: ({ color, size }) => <Ionicons name="search" color={color} size={size} />,
        }}
      />
       <Tabs.Screen
        name="chat" // New Chat screen
        options={{
          title: 'Chat',
          tabBarIcon: ({ color, size }) => <Ionicons name="chatbubbles-outline" color={color} size={size} />,
        }}
      />
    </Tabs>
  );
}
