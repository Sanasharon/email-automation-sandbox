import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 w-full h-full flex flex-col items-center justify-center bg-surface text-on-surface">
          <div className="bg-error-container text-on-error-container p-6 rounded-xl max-w-lg shadow-sm border border-error/20">
            <h2 className="text-xl font-headline-md mb-2 flex items-center gap-2">
              <span className="material-symbols-outlined">error</span>
              Module Crash Detected
            </h2>
            <p className="text-body-md mb-4">
              A critical rendering error occurred in this section. Other modules remain unaffected.
            </p>
            <div className="bg-surface-container rounded p-3 text-xs overflow-auto max-h-32 mb-4 font-mono text-on-surface-variant">
              {this.state.error?.message || "Unknown error"}
            </div>
            <button 
              onClick={() => this.setState({ hasError: false })}
              className="bg-primary text-on-primary px-4 py-2 rounded-full font-label-bold hover:bg-primary/90 transition-colors"
            >
              Attempt Recovery
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
