const webpack = require('webpack'); // eslint-disable-line no-var
const pkg = require('./package.json');


module.exports = {
  entry: {
    vendor: Object.keys(pkg.dependencies),
    build: './app.js'
  },
  output: {
    // filename: '[name].[chunkhash].js'
    filename: '[name].js'
  },
  // devtool: 'source-map',
  module: {
    loaders: [
      {
        exclude: /node_modules/,
        loader: 'babel'
      }
    ]
  },
  devServer: {
    historyApiFallback: true,
    hot: true,
    inline: true,
    progress: true,

    // display only errors to reduce the amount of output
    stats: 'errors-only'

    // parse host and port from env so this is easy
    // to customize
    // host: process.env.HOST,
    // port: process.env.PORT
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin(
        'vendor',
        // '[name].[chunkhash].js'
        '[name].js'
      ),
    new webpack.HotModuleReplacementPlugin()

    // // Use this only in production
    // new webpack.DefinePlugin({
    //   'process.env': {
    //     NODE_ENV: JSON.stringify('production')
    //   }
    // }),
    // new webpack.optimize.UglifyJsPlugin({
    //   compress: {
    //     warnings: false
    //   }
    // })
  ]
};
