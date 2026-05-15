export interface ExampleProblem {
  id: string;
  label: string;
  pattern: string;
  text: string;
}

export const EXAMPLE_PROBLEMS: ExampleProblem[] = [
  {
    id: "sliding-window",
    label: "Sliding Window",
    pattern: "Sliding Window",
    text: "Given an array of positive integers and a positive integer k, find the maximum sum of any contiguous subarray of size k.",
  },
  {
    id: "binary-search",
    label: "Binary Search",
    pattern: "Binary Search",
    text: "You are given a sorted array of integers and a target value. Return the index if the target is found, otherwise return -1. Must run in O(log n).",
  },
  {
    id: "dynamic-programming",
    label: "Dynamic Programming",
    pattern: "Dynamic Programming",
    text: "Given an integer array nums, return the length of the longest strictly increasing subsequence.",
  },
  {
    id: "graph-bfs",
    label: "Graph BFS",
    pattern: "Graph / BFS / DFS",
    text: "Given a 2D grid of '1's (land) and '0's (water), count the number of islands. An island is surrounded by water and formed by connecting adjacent lands horizontally or vertically.",
  },
  {
    id: "two-pointers",
    label: "Two Pointers",
    pattern: "Two Pointers",
    text: "Given a sorted array of integers, find two numbers such that they add up to a specific target. Return indices of the two numbers.",
  },
  {
    id: "backtracking",
    label: "Backtracking",
    pattern: "Recursion / Backtracking",
    text: "Given a collection of distinct integers, return all possible permutations. You can return the answer in any order.",
  },
];
