{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}

module Main where

import Network.Wreq
import Control.Lens
import Data.Aeson
import GHC.Generics
import System.Environment (getArgs)

data WordOutput = WordOutput
  { word :: String
  } deriving (Show, Generic)

instance FromJSON WordOutput

convert :: [a] -> a
convert [x] = x


main :: IO ()
main = do
    searchWord2 <- getArgs
    let searchWord = convert searchWord2
    
    let url = "https://api.datamuse.com/words?sp=" ++ searchWord
    response <- get url

    let decodedResponse = decode (response ^. responseBody) :: Maybe [WordOutput]

    let firstWord = maybe "Failed" word (fmap head decodedResponse)
    
    putStrLn $ "@@OUTPUT:" ++ firstWord

