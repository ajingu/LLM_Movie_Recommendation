import { Tabs } from 'expo-router';
import React from 'react';

// If you want icons, you'll need to install an icon library like @expo/vector-icons
// import { Ionicons } from '@expo/vector-icons'; 

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        // Example styling - adjust as needed
        // tabBarActiveTintColor: 'blue',
      }}>
      <Tabs.Screen
        name="index" // Search screen
        options={{
          title: 'Search',
          // Example Icon:
          // tabBarIcon: ({ color, size }) => <Ionicons name="search" color={color} size={size} />,
        }}
      />
       <Tabs.Screen
        name="chat" // New Chat screen
        options={{
          title: 'Chat',
           // Example Icon:
          // tabBarIcon: ({ color, size }) => <Ionicons name="chatbubbles-outline" color={color} size={size} />,
        }}
      />
    </Tabs>
  );
}
