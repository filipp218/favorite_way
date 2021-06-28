import yaml

favorite_way_get = yaml.safe_load(
    """
      type: object
      additionalProperties: false
      properties:
        user_id:
          type: integer
        location1:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
        location2:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
        install_date:
          type: string
          example: '2021-06-29 12:42:10.940759'
      required:
        - location1
        - location2
        - install_date
        """)

favorite_way_get400 = yaml.safe_load(
    """
      type: object
      properties:
        user_id:
          type: integer
        favorite_way:
          type: boolean
      required:
        - user_id
        - favorite_way
        """)

favorite_way_post = yaml.safe_load(
    """
      type: object
      additionalProperties: false
      properties:
        location1:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
          required:
            - lat
            - long
        location2:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
          required:
            - lat
            - long
        install_date:
          type: string
          example: '2021-06-29 12:42:10.940759'
      required:
        - location1
        - location2
        - install_date                                       
        """
    )

favorite_way_post201 = yaml.safe_load(
    """
      type: object
      additionalProperties: false
      properties:
        user_id:
          type: integer
    """)

check_favorite_way = yaml.safe_load(
    """
      type: object
      additionalProperties: false
      properties:
        user_id:
          type: integer
        location1:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
        location2:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
      required:
        - user_id
        - location1
        - location2
    """)

check_favorite_way200 = yaml.safe_load(
    """
      type: object
      additionalProperties: false
      properties:
        user_id:
          type: integer
        location1:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
        location2:
          type: object
          properties:
            lat:
              type: number
            long:
              type: number
        favorite_way:
          type: boolean
      required:
        - user_id
        - location1
        - location2
        - favorite_way
    """)
