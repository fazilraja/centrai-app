import { useEffect, useState } from 'react';

/**
 * Theme type definition
 * - light: Light mode with warm parchment background
 * - dark: Dark mode with charcoal background
 * - system: Follows system preference
 */
export type Theme = 'light' | 'dark' | 'system';

/**
 * Hook for managing theme state with localStorage persistence and system preference detection.
 * 
 * Features:
 * - Persists theme preference to localStorage
 * - Detects system color scheme preference
 * - Automatically updates when system preference changes
 * - Applies theme class to document root
 * 
 * @returns {object} Theme state and setter
 * @returns {Theme} theme - Current theme preference (light/dark/system)
 * @returns {function} setTheme - Function to update theme
 * @returns {Theme} effectiveTheme - Resolved theme after system detection (light/dark only)
 * 
 * @example
 * ```tsx
 * const { theme, setTheme, effectiveTheme } = useTheme();
 * 
 * // Set theme
 * setTheme('dark');
 * 
 * // Check current effective theme
 * console.log(effectiveTheme); // 'dark' or 'light'
 * ```
 */
export function useTheme() {
  // Initialize theme from localStorage or default to 'system'
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('centrai-theme') as Theme;
      return stored || 'system';
    }
    return 'system';
  });

  /**
   * Gets the effective theme (light or dark) based on current preference.
   * If theme is 'system', detects system preference.
   * 
   * @returns {Theme} The resolved theme ('light' or 'dark')
   */
  const getEffectiveTheme = (): 'light' | 'dark' => {
    if (theme === 'system') {
      // Detect system preference
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return 'light'; // Default fallback
    }
    return theme;
  };

  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>(getEffectiveTheme);

  /**
   * Sets the theme preference and persists to localStorage.
   * 
   * @param {Theme} newTheme - The theme to set ('light', 'dark', or 'system')
   */
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    if (typeof window !== 'undefined') {
      localStorage.setItem('centrai-theme', newTheme);
    }
  };

  // Effect to apply theme class to document and handle system preference changes
  useEffect(() => {
    const root = document.documentElement;
    const effective = getEffectiveTheme();
    setEffectiveTheme(effective);

    // Remove both classes first
    root.classList.remove('light', 'dark');
    
    // Add the effective theme class
    root.classList.add(effective);

    // Listen for system theme changes when in 'system' mode
    if (theme === 'system' && typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      /**
       * Handler for system theme preference changes.
       * Updates effective theme when system preference changes.
       */
      const handleChange = (e: MediaQueryListEvent) => {
        const newEffective = e.matches ? 'dark' : 'light';
        setEffectiveTheme(newEffective);
        root.classList.remove('light', 'dark');
        root.classList.add(newEffective);
      };

      // Add listener for changes (using addEventListener for better compatibility)
      mediaQuery.addEventListener('change', handleChange);
      
      // Cleanup listener on unmount
      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    }
  }, [theme]);

  return {
    theme,
    setTheme,
    effectiveTheme,
  };
}

